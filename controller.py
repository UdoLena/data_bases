# controller.py
import os
from model import DBError
import view

class Controller:
    def __init__(self, model):
        self.model = model

    def show_tables(self):
        try:
            tables, ms = self.model.get_tables()
            print(f"Query time: {ms:.2f} ms")
            view.print_list(tables)
        except DBError as e:
            print("DB error:", e)

    def show_columns_types(self):
        t = input("Enter table name: ").strip()
        try:
            rows, ms = self.model.get_columns_with_types(t)
            print(f"Time: {ms:.2f} ms")
            for r in rows:
                print(f"{r['column_name']} — {r['data_type']}")
        except DBError as e:
            print("DB error:", e)

    def show_columns_only(self):
        t = input("Enter table name: ").strip()
        try:
            cols, ms = self.model.get_columns_only(t)
            print(f"Time: {ms:.2f} ms")
            view.print_list(cols)
        except DBError as e:
            print("DB error:", e)

    def view_rows(self):
        t = input("Enter table name: ").strip()
        try:
            limit = int(input("Enter limit (default 20): ") or 20)
            rows, ms = self.model.list_rows(t, limit)
            print(f"Time: {ms:.2f} ms")
            view.print_rows(rows)
        except ValueError:
            print("Invalid limit.")
        except DBError as e:
            print("DB error:", e)

    def show_fks(self):
        t = input("Enter table name: ").strip()
        try:
            rows, ms = self.model.get_foreign_keys(t)
            print(f"Time: {ms:.2f} ms")
            if not rows:
                print("No foreign keys.")
            else:
                for r in rows:
                    print(f"{r['column_name']} -> {r['foreign_table']}({r['foreign_column']})")
        except DBError as e:
            print("DB error:", e)

    def execute_sql_file(self):
        path = input("Enter SQL file name (e.g. exhibit.sql): ").strip()
        if not os.path.exists(path):
            print("File not found.")
            return
        try:
            ms = self.model.execute_sql_file(path)
            print(f"Script executed successfully in {ms:.2f} ms")
        except DBError as e:
            print("DB error:", e)

    def insert_row(self):
        t = input("Enter table name: ").strip()
        try:
            cols, _ = self.model.get_columns_only(t)
            data = view.prompt_row_values(cols)
            ms = self.model.insert_row(t, data)
            print(f"Inserted. Time: {ms:.2f} ms")
        except DBError as e:
            print("DB error:", e)

    def update_rows(self):
        t = input("Enter table name: ").strip()
        set_dict = view.prompt_set_clause()
        if not set_dict:
            print("No changes.")
            return
        where = input("Enter WHERE condition (e.g. id=1): ").strip()
        if not where:
            print("WHERE required.")
            return
        try:
            ms = self.model.update_rows(t, set_dict, where)
            print(f"Updated. Time: {ms:.2f} ms")
        except DBError as e:
            print("DB error:", e)

    def delete_by_pk(self):
        t = input("Enter table name: ").strip()
        try:
            pk_cols, _ = self.model.get_primary_key(t)
            if not pk_cols:
                print("No PK in table.")
                return
            print("PK columns:", pk_cols)
            vals = {}
            for c in pk_cols:
                v = input(f"{c}: ").strip()
                vals[c] = v
            ms = self.model.delete_by_pk(t, vals)
            print(f"Deleted. Time: {ms:.2f} ms")
        except DBError as e:
            print("DB error:", e)

    def delete_all(self):
        t = input("Enter table name: ").strip()
        confirm = input(f"Truncate {t}? (y/n): ").strip().lower()
        if confirm not in ('y', 'yes'):
            print("Cancelled.")
            return
        try:
            ms = self.model.truncate_table(t)
            print(f"Table cleared in {ms:.2f} ms")
        except DBError as e:
            print("DB error:", e)

    def complex1(self):
        try:
            y1 = int(input("Start year: "))
            y2 = int(input("End year: "))
            pat = input("Author last name pattern (%): ") or '%'
            rows, ms = self.model.complex_query_1((y1, y2, pat))
            print(f"Time: {ms:.2f} ms")
            view.print_rows(rows)
        except (ValueError, DBError) as e:
            print("Error:", e)

    def complex2(self):
        pat = input("Room name pattern (%): ") or '%'
        try:
            rows, ms = self.model.complex_query_2((pat,))
            print(f"Time: {ms:.2f} ms")
            view.print_rows(rows)
        except DBError as e:
            print("DB error:", e)

    def complex3(self):
        try:
            mat = input("Materials pattern (%): ") or '%'
            y1 = int(input("Start year: "))
            y2 = int(input("End year: "))
            rows, ms = self.model.complex_query_3((mat, y1, y2))
            print(f"Time: {ms:.2f} ms")
            view.print_rows(rows)
        except (ValueError, DBError) as e:
            print("Error:", e)
