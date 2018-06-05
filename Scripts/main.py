from Data import DataBase
import datetime

Lib = DataBase()
Lib.get_connection("root", "1234", '127.0.0.1', 'Test_base')
#Lib.check_database("Test_base")
#Lib.create_tables()
#Lib.add_string("Orders", (1, 1, datetime.date(2012, 3, 23),datetime.date(2013, 3, 23)))
Lib.load_data("'C:/Work/Data/readers.csv'","Readers")
#Lib.save_data("'C:/Work2/Data5.csv'")
#Lib.Max('books')
#l = Lib.get_strings('books')
#l = Lib.table_list()
Lib.close_all()