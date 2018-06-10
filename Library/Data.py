import mysql.connector
import datetime
from mysql.connector import errorcode


class DataBase:

    def __init__(self):
        self.cnx = ''
        self.cursor = ''
        self.Tables = {}
        self.connected = False
        self.keys = {"Books": ["(id,name,author,year,publishing_home)", "(%s, %s, %s, %s, %s)"],
                     "Readers": ["(id,name,telephone_number,year_of_birth)", "(%s, %s, %s, %s)"],
                     "Orders": ["(id,book_id,reader_id,date_of_issue,return_date)", "(%s, %s, %s, %s, %s)"]}

    def get_connection(self, name, password, host, db = ''):
        self.cnx = mysql.connector.connect(user=name, password=password,
                                      host=host, database = db)
        self.cursor = self.cnx.cursor()
        self.connected = True

    def create_database(self, DB_NAME):
        try:
            self.cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
            return True, None
        except mysql.connector.Error as err:
            return False, "Failed creating database: {}".format(err)

    def check_database(self, DB_NAME):
        try:
            self.cnx.database = DB_NAME
            return True, None
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.create_database(DB_NAME)
                self.cnx.database = DB_NAME
                return True, None
            else:
                return False ,err

    def create_tables(self):
        self.Tables["Books"] = ("CREATE TABLE `Books`("
                           "`id` SERIAL,"
                           "`name` VARCHAR(70),"
                           "`author` VARCHAR(40),"
                           "`year` INT,"
                           "`publishing_home` VARCHAR(50),"
                           "PRIMARY KEY (`id`)"
                           ")ENGINE InnoDB CHARACTER SET utf8")
        self.Tables["Readers"] = (("CREATE TABLE `Readers`("
                           "`id` SERIAL,"
                           "`name` VARCHAR(70),"
                           "`telephone_number` VARCHAR(20),"
                           "`year_of_birth` BIGINT(20),"
                           "PRIMARY KEY (`id`)"
                           ")ENGINE InnoDB CHARACTER SET utf8"))
        self.Tables["Orders"] = (("CREATE TABLE `orders`("
                            "`id` SERIAL,"
                            "`book_id` BIGINT UNSIGNED NOT NULL,"
                            "`reader_id` BIGINT UNSIGNED NOT NULL,"
                            "`date_of_issue` DATE,"
                            "`return_date` DATE,"
                            "PRIMARY KEY (`id`),"
                            "FOREIGN KEY (book_id) REFERENCES books (id)"
                            "ON DELETE RESTRICT ON UPDATE CASCADE,"
                            "FOREIGN KEY (reader_id) REFERENCES readers (id)"
                            "ON DELETE RESTRICT ON UPDATE CASCADE"
                           ")ENGINE InnoDB CHARACTER SET utf8"))


        for name, ddl in self.Tables.items():
            try:
                print("Creating table {}: ".format(name), end='')
                self.cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")

    def add_string(self, Table, data):
        if Table in self.keys:
            insert_stmt = ("INSERT INTO {0} {1} "
                        "VALUES {2} ".format(Table, self.keys[Table][0], self.keys[Table][1] ))
            self.cursor.execute(insert_stmt, data)
            self.cnx.commit()

    def load_data(self, Path, Table):
        k = self.get_strings(Table)
        if self.get_strings(Table) == [] :
            if Table in self.keys:
                extension = Path[Path.find('.'):]
                if extension == ".txt'":
                    load_stmt = ("LOAD DATA INFILE {0} "
                                 "INTO TABLE {1} CHARACTER SET cp1251" .format(Path, Table))
                    self.cursor.execute(load_stmt)
                    self.cnx.commit()
                elif extension == ".csv'":
                    load_stmt = ("LOAD DATA INFILE {0}  "
                                "INTO TABLE {1} FIELDS TERMINATED BY ',' "
                                 "LINES TERMINATED BY '\n' "
                                 "IGNORE 1 ROWS ".format(Path, Table))
                    print(load_stmt)
                    self.cursor.execute(load_stmt)
                    self.cnx.commit()
        else:
            self.DEL(Table)
            self.load_data(Path, Table)

    def DEL(self, table, value = '*'):
        if value == '*':
            if not (table == "Orders"):
                del_stmt = ("DELETE  FROM {}".format("Orders"))
                self.cursor.execute(del_stmt)
                self.cnx.commit()

            del_stmt = ("DELETE  FROM {}".format(table))
        else:
            if table == "Books":
                Orders = self.get_strings("Orders")
                i = 0
                flag = True
                while i < (len(Orders)) and flag:
                    if value == Orders[i][1]:
                        flag = False
                        del_stmt = ("DELETE FROM {} WHERE id = {}".format("Orders", Orders[i][0]))
                        self.cursor.execute(del_stmt)
                        self.cnx.commit()
                    i+=1

            if table == "Readers":
                Orders = self.get_strings("Orders")
                i = 0
                flag = True
                while i < (len(Orders)) and flag:
                    if value == Orders[i][2]:
                        flag = False
                        del_stmt = ("DELETE FROM {} WHERE id = {}".format("Orders", Orders[i][0]))
                        self.cursor.execute(del_stmt)
                        self.cnx.commit()
                i+=1

            del_stmt = ("DELETE FROM {} WHERE id = {}".format(table, value))
        self.cursor.execute(del_stmt)
        self.cnx.commit()

    def Change_data(self,table, field, id, value, Type):
        if Type == "str":
            value = "'" + value +"'"
        change_stmt = ("UPDATE {} SET {}={} WHERE id={}".format(table, field, value, id))
        self.cursor.execute(change_stmt)
        self.cnx.commit()

    def save_data(self, Path, Table):
        if Table in self.keys:
            extension = Path[Path.find('.'):]
            if extension == ".txt'":
                save_stmt = ("SELECT * FROM {0} INTO OUTFILE {1}".format(Path, Table))
                self.cursor.execute(save_stmt)
                self.cnx.commit()
            elif extension == ".csv'":
                save_stmt = ("SELECT * FROM {0} INTO OUTFILE {1} "
                             "FIELDS TERMINATED BY ',' "
                             "LINES TERMINATED BY '\n'".format(Table,Path))
                self.cursor.execute(save_stmt)
                self.cnx.commit()

    def Max(self,table):
        max_stmt = ("SELECT MAX(id) AS id FROM {}".format(table))
        self.cursor.execute(max_stmt)
        try:
            return int(self.cursor.fetchall()[0][0])
        except:
            return False

    def get_strings(self,table):
        all_str = ("SELECT * FROM {}".format(table))
        self.cursor.execute(all_str)
        return self.cursor.fetchall()

    def rename_column(self, table, old_name, new_name, Type):
        if Type == 'str':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {} ".format(table, old_name, new_name, "VARCHAR(100)"))
        if Type == 'int':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {}".format(table, old_name, new_name, "INT"))
        if Type =='date':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {}".format(table, old_name, new_name, "DATE"))
        self.cursor.execute(rename_stmt)
        self.cnx.commit()

    def table_list(self, name, password, host):
        self.get_connection(name, password, host)
        self.cursor.execute("SHOW DATABASES")
        lst = self.cursor.fetchall()
        new_lst = [value[0] for value in lst]
        bases = []
        for base in new_lst:
            tables = self.Show_tables(name, password, host, base)
            if "books" in tables and "readers" in tables and "orders" in tables:
                bases.append(base)
        return bases

    def Show_tables(self, name, password, host, bd):
        self.cursor.execute("SHOW TABLES FROM {}".format(bd))
        return [value[0] for value in self.cursor.fetchall()]

    def Del_db(self, db_name):
        del_stmt = "DROP DATABASE {}".format(db_name)
        self.cursor.execute(del_stmt)
        self.cnx.commit()

    def close_all(self):
        if self.connected:
            self.cursor.close()
            self.cnx.close()
            self.connected = False

