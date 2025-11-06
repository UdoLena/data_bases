# model.py
import psycopg2
from psycopg2 import sql, extras
from contextlib import contextmanager
import time

class DBError(Exception):
    pass

class Model:
    def __init__(self, db_config, schema='public'):
        self.db_config = db_config
        self.schema = schema

    @contextmanager
    def get_conn(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
        except psycopg2.Error as e:
            raise DBError(str(e))
        finally:
            if conn:
                conn.close()

    def _exec(self, query, params=None, fetch=False):
        start = time.perf_counter()
        with self.get_conn() as conn:
            try:
                with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                    cur.execute(query, params)
                    rows = cur.fetchall() if fetch else None
                    conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                raise DBError(str(e))
        ms = (time.perf_counter() - start) * 1000
        return rows, ms

    # -------- системна інформація --------
    def get_tables(self):
        q = """SELECT table_name
               FROM information_schema.tables
               WHERE table_schema = %s
                 AND table_type = 'BASE TABLE'
               ORDER BY table_name;"""
        rows, ms = self._exec(q, (self.schema,), fetch=True)
        return [r['table_name'] for r in rows], ms

    def get_columns_with_types(self, table):
        q = """SELECT column_name, data_type, character_maximum_length
               FROM information_schema.columns
               WHERE table_schema=%s AND table_name=%s
               ORDER BY ordinal_position;"""
        return self._exec(q, (self.schema, table), fetch=True)

    def get_columns_only(self, table):
        rows, ms = self.get_columns_with_types(table)
        return [r['column_name'] for r in rows], ms

    def get_primary_key(self, table):
        q = """SELECT kcu.column_name
               FROM information_schema.table_constraints tc
               JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name=kcu.constraint_name
               WHERE tc.constraint_type='PRIMARY KEY'
                 AND tc.table_schema=%s AND tc.table_name=%s;"""
        rows, ms = self._exec(q, (self.schema, table), fetch=True)
        return [r['column_name'] for r in rows], ms

    def get_foreign_keys(self, table):
        q = """SELECT
                 kcu.column_name AS column_name,
                 ccu.table_name AS foreign_table,
                 ccu.column_name AS foreign_column
               FROM information_schema.table_constraints tc
               JOIN information_schema.key_column_usage kcu
                 ON tc.constraint_name = kcu.constraint_name
               JOIN information_schema.constraint_column_usage ccu
                 ON ccu.constraint_name = tc.constraint_name
               WHERE tc.constraint_type = 'FOREIGN KEY'
                 AND tc.table_schema = %s
                 AND tc.table_name = %s;"""
        return self._exec(q, (self.schema, table), fetch=True)

    # -------- базові CRUD --------
    def list_rows(self, table, limit=20):
        q = sql.SQL("SELECT * FROM {}.{} LIMIT %s").format(
            sql.Identifier(self.schema), sql.Identifier(table))
        return self._exec(q, (limit,), fetch=True)

    def insert_row(self, table, data):
        cols = list(data.keys())
        vals = [data[c] for c in cols]
        q = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
            sql.Identifier(self.schema),
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, cols)),
            sql.SQL(', ').join(sql.Placeholder() * len(cols)))
        return self._exec(q, vals, fetch=False)[1]

    def update_rows(self, table, set_dict, where_clause):
        sets = [sql.SQL("{}=%s").format(sql.Identifier(k)) for k in set_dict.keys()]
        q = sql.SQL("UPDATE {}.{} SET {} WHERE " + where_clause).format(
            sql.Identifier(self.schema),
            sql.Identifier(table),
            sql.SQL(', ').join(sets))
        vals = list(set_dict.values())
        return self._exec(q, vals, fetch=False)[1]

    def delete_by_pk(self, table, pk_vals):
        conds = [sql.SQL("{}=%s").format(sql.Identifier(k)) for k in pk_vals.keys()]
        q = sql.SQL("DELETE FROM {}.{} WHERE ").format(
            sql.Identifier(self.schema), sql.Identifier(table)) + sql.SQL(' AND ').join(conds)
        return self._exec(q, list(pk_vals.values()), fetch=False)[1]

    def truncate_table(self, table):
        q = sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY CASCADE").format(
            sql.Identifier(self.schema), sql.Identifier(table))
        return self._exec(q, fetch=False)[1]

    # -------- виконання SQL файлу --------
    def execute_sql_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            sql_text = f.read()
        start = time.perf_counter()
        with self.get_conn() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql_text)
                    conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                raise DBError(str(e))
        return (time.perf_counter() - start) * 1000

    # -------- складні запити --------
    def complex_query_1(self, params):
        q = f"""SELECT a.author_id, a.first_name||' '||a.last_name AS author_name,
                       e.type, COUNT(*) AS exhibits_count
                FROM {self.schema}.exhibit e
                JOIN {self.schema}.author a ON e.author_id=a.author_id
                WHERE e.year BETWEEN %s AND %s AND a.last_name ILIKE %s
                GROUP BY a.author_id, author_name, e.type
                ORDER BY exhibits_count DESC;"""
        return self._exec(q, params, fetch=True)

    def complex_query_2(self, params):
        q = f"""SELECT r.floor, r.name AS room_name,
                       COUNT(p.exhibit_id) AS exhibits_in_room,
                       AVG(e.year)::int AS avg_year
                FROM {self.schema}.room r
                JOIN {self.schema}.placement p ON r.room_id=p.room_id
                JOIN {self.schema}.exhibit e ON p.exhibit_id=e.exhibit_id
                WHERE r.name ILIKE %s
                GROUP BY r.floor, r.name
                ORDER BY r.floor, exhibits_in_room DESC;"""
        return self._exec(q, params, fetch=True)

    def complex_query_3(self, params):
        q = f"""SELECT e.materials, COUNT(*) AS cnt,
                       MIN(e.year) AS first_year, MAX(e.year) AS last_year
                FROM {self.schema}.exhibit e
                WHERE e.materials ILIKE %s AND e.year BETWEEN %s AND %s
                GROUP BY e.materials ORDER BY cnt DESC;"""
        return self._exec(q, params, fetch=True)
