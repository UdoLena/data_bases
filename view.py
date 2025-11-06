# view.py
def print_menu():
    print("\n=== MUSEUM DB CONSOLE ===")
    print("1. Show tables")
    print("2. Show columns and types for a table")
    print("3. Show column names only")
    print("4. View table rows (LIMIT)")
    print("5. Show foreign keys for a table")
    print("6. Execute SQL file (e.g. exhibit.sql)")
    print("7. Insert one row to a table")
    print("8. Update rows in a table")
    print("9. Delete row by primary key")
    print("10. Delete ALL data from a table")
    print("11. Complex query #1")
    print("12. Complex query #2")
    print("13. Complex query #3")
    print("0. Exit")

def print_rows(rows):
    if not rows:
        print("[No rows]")
        return
    keys = rows[0].keys()
    header = " | ".join(keys)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(r[k]) for k in keys))

def print_list(lst):
    if not lst:
        print("[empty]")
        return
    for item in lst:
        print("-", item)

def prompt_row_values(cols):
    print("Enter values for columns (blank = NULL):")
    res = {}
    for c in cols:
        val = input(f"{c}: ").strip()
        res[c] = None if val == "" else val
    return res

def prompt_set_clause():
    print("Enter updates (column=value), empty line to stop:")
    d = {}
    while True:
        s = input("set> ").strip()
        if not s: break
        if '=' not in s:
            print("Format must be column=value")
            continue
        col, val = s.split('=', 1)
        d[col.strip()] = val.strip()
    return d
