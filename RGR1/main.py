# main.py
import config
from model import Model
from controller import Controller
import view

def main():
    model = Model(config.DB, schema='public')
    ctrl = Controller(model)

    while True:
        view.print_menu()
        choice = input("Select > ").strip()
        match choice:
            case '1': ctrl.show_tables()
            case '2': ctrl.show_columns_types()
            case '3': ctrl.show_columns_only()
            case '4': ctrl.view_rows()
            case '5': ctrl.show_fks()
            case '6': ctrl.execute_sql_file()
            case '7': ctrl.insert_row()
            case '8': ctrl.update_rows()
            case '9': ctrl.delete_by_pk()
            case '10': ctrl.delete_all()
            case '11': ctrl.complex1()
            case '12': ctrl.complex2()
            case '13': ctrl.complex3()
            case '0':
                print("Bye!")
                break
            case _:
                print("Invalid option.")

if __name__ == "__main__":
    main()

