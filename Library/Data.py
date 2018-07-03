import mysql.connector
import datetime

class DataBase:
    """
    Автор:Сорокин Н.А
    Класс реализует базу данных
    """

    def __init__(self):
        """
        Автор:Сорокин Н.А
        Конструктор класса
        """
        self.cnx = ''
        self.cursor = ''
        self.Tables = {}
        self.connected = False
        self.keys = {"Books": ["(id,name,author,year,publishing_home)", "(%s, %s, %s, %s, %s)"],
                     "Readers": ["(id,name,telephone_number,year_of_birth)", "(%s, %s, %s, %s)"],
                     "Orders": ["(id,book_id,reader_id,date_of_issue,return_date)", "(%s, %s, %s, %s, %s)"]}

    def get_connection(self, name, password, host, db = ''):
        """
        Автор:Сорокин Н.А
        Метод подключает к базе данных MySQL
        :param name: Логин пользователя
        :param password: Пароль пользователя
        :param host: IP адрес хоста
        :param db: Имя базы данных
        :return:
        """
        self.cnx = mysql.connector.connect(user=name, password=password,
                                      host=host, database = db)
        self.cursor = self.cnx.cursor()
        self.connected = True # подключеие прошло успешно

    def create_database(self, DB_NAME):
        """
        Автор:Сорокин Н.А
        Метод создающий базу данных
        :param DB_NAME:Имя базы данных
        :return:
        """
        try:
            self.cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET cp1251".format(DB_NAME))
            return True, None
        except mysql.connector.Error as err:
            return False, "Failed creating database: {}".format(err)

    def check_database(self, DB_NAME):
        """
        Автор:Сорокин Н.А
        Метод проверяет свободно ли имя базы данных
        :param DB_NAME:
        :return:
        """
        try:
            self.cnx.database = DB_NAME
            return True, None
        except:
            try:
                self.create_database(DB_NAME)
                self.cnx.database = DB_NAME
                return True, None
            except:
                return False ,"Fail"

    def create_tables(self):
        """
        Автор:Сорокин Н.А
        Метод создаёт таблицы
        :return:
        """
        self.Tables["Books"] = ("CREATE TABLE `Books`("
                           "`id` SERIAL,"
                           "`name` VARCHAR(70),"
                           "`author` VARCHAR(40),"
                           "`year` INT,"
                           "`publishing_home` VARCHAR(50),"
                           "PRIMARY KEY (`id`)"
                           ")ENGINE InnoDB CHARACTER SET cp1251")
        self.Tables["Readers"] = (("CREATE TABLE `Readers`("
                           "`id` SERIAL,"
                           "`name` VARCHAR(70),"
                           "`telephone_number` VARCHAR(20),"
                           "`year_of_birth` BIGINT(20),"
                           "PRIMARY KEY (`id`)"
                           ")ENGINE InnoDB CHARACTER SET cp1251"))
        self.Tables["Orders"] = (("CREATE TABLE `Orders`("
                            "`id` SERIAL,"
                            "`book_id` BIGINT UNSIGNED NOT NULL,"
                            "`reader_id` BIGINT UNSIGNED NOT NULL,"
                            "`date_of_issue` DATE,"
                            "`return_date` DATE,"
                            "PRIMARY KEY (`id`),"
                            "FOREIGN KEY (book_id) REFERENCES Books (id)"
                            "ON DELETE RESTRICT ON UPDATE CASCADE,"
                            "FOREIGN KEY (reader_id) REFERENCES Readers (id)"
                            "ON DELETE RESTRICT ON UPDATE CASCADE"
                           ")ENGINE InnoDB CHARACTER SET cp1251"))


        for name, ddl in self.Tables.items():
            try:
                print("Creating table {}: ".format(name), end='')
                self.cursor.execute(ddl)
            except :
                    print("already exists.")

            else:
                print("OK")

    def add_string(self, Table, data):
        """
        Автор:Сорокин Н.А
        Метод добавляет строку в таблицу
        :param Table:Имя таблицы
        :param data:Данные, которые пользователь хочет вставить в таблицу
        :return:
        """
        if Table in self.keys:# Проверка названия таблицы
            insert_stmt = ("INSERT INTO {0} {1} "
                        "VALUES {2} ".format(Table, self.keys[Table][0], self.keys[Table][1] ))
            self.cursor.execute(insert_stmt, data)
            self.cnx.commit()

    def load_data(self, Path, Table):
        """
        Автор:Сорокин Н.А
        Метод реализует загрузку данных из файла в базу данных
        :param Path:Путь до файла
        :param Table: Имя таблицы
        :return:
        """
        if self.get_strings(Table) == [] :# проверяем наличие данных в выбранной таблице
            if Table in self.keys:# Проверка названия таблицы
                #проверяем расширение выбранного файла
                extension = Path[Path.find('.'):]
                if extension == ".txt'":
                    load_stmt = ("LOAD DATA LOCAL INFILE {0} "
                                 "INTO TABLE {1} CHARACTER SET cp1251" .format(Path, Table))
                    self.cursor.execute(load_stmt)
                    self.cnx.commit()
                elif extension == ".csv'":
                    # Задаём параметры обработки информации соответсвующие csv файлу
                    load_stmt = ("LOAD DATA LOCAL INFILE {0} "
                                "INTO TABLE {1} CHARACTER SET cp1251 FIELDS TERMINATED BY ',' "
                                 "LINES TERMINATED BY '\n' "
                                 "IGNORE 1 ROWS ".format(Path, Table))
                    print(load_stmt)
                    self.cursor.execute(load_stmt)
                    self.cnx.commit()
        else:
            self.DEL(Table)# Удаляем данные
            self.load_data(Path, Table)

    def DEL(self, table, value = '*'):
        """
        Автор:Сорокин Н.А
        Удаляет данные из базы данных
        :param table:Название таблицы
        :param value:ID удаляемых данных, по умолчанию удаляет все данные
        :return:
        """
        if value == '*':# Если данные по умолчанию
            if not (table == "Orders"):
                del_stmt = ("DELETE  FROM {}".format("Orders"))
                self.cursor.execute(del_stmt)
                self.cnx.commit()

            del_stmt = ("DELETE  FROM {}".format(table))
        else:
            # Проверяем есть ли связанные c Orders id в Books и Tables
            if table == "Books":
                Orders = self.get_strings("Orders")
                i = 0
                flag = True
                while i < (len(Orders)) and flag:
                    if value == Orders[i][1]:
                        flag = False
                        del_stmt = ("DELETE FROM {} WHERE id = {}".format("Orders", Orders[i][0]))
                        self.cursor.execute(del_stmt)# удаляем связанные ID из Orders
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
                        self.cursor.execute(del_stmt)# удаляем связанные ID из Orders
                        self.cnx.commit()
                i+=1

            del_stmt = ("DELETE FROM {} WHERE id = {}".format(table, value))
        self.cursor.execute(del_stmt)# удаляем данные
        self.cnx.commit()

    def Change_data(self,table, field, id, value, Type):
        """
        Автор:Сорокин Н.А
        Метод меняющий данные в таблице по заданным значениям
        :param table:Имя таблицы
        :param field:Изменяемое поле
        :param id:ID изменяемого поля
        :param value:Изменяемые данные
        :param Type: Тип данных
        :return:
        """
        if Type == "str":
            value = "'" + value +"'" # данные строкового типа должны быть в кавычках
        change_stmt = ("UPDATE {} SET {}={} WHERE id={}".format(table, field, value, id))
        self.cursor.execute(change_stmt)
        self.cnx.commit()

    def save_data(self, Path, Table):
        """
        Автор:Сорокин Н.А
        Метод сохраняет данные в файл
        :param Path:Путь до файла
        :param Table:Имя таблицы
        :return:
        """
        if Table in self.keys:
            extension = Path[Path.find('.'):]# Проверяем расширение файла
            if extension == ".txt'":
                save_stmt = ("SELECT * FROM {0} INTO OUTFILE {1}".format(Path, Table))
                self.cursor.execute(save_stmt)
                self.cnx.commit()
            elif extension == ".csv'":
                # Задаём параметры обработки информации соответсвующие csv файлу
                save_stmt = ("SELECT * FROM {0} INTO OUTFILE {1} "
                             "FIELDS TERMINATED BY ',' "
                             "LINES TERMINATED BY '\n'".format(Table,Path))
                self.cursor.execute(save_stmt)
                self.cnx.commit()

    def Max(self,table):
        """
        Автор:Сорокин Н.А
        Метод находит максимум
        :param table:Имя таблицы
        :return:Возращает максимум или False, если максимума нет
        """
        max_stmt = ("SELECT MAX(id) AS id FROM {}".format(table))
        self.cursor.execute(max_stmt)
        try:
            return int(self.cursor.fetchall()[0][0])
        except:
            return False

    def get_strings(self,table):
        """
        Автор:Сорокин Н.А
        Считывает всю информацию из таблицы
        :param table:Имя таблицы
        :return: Возвращает кортеж данных из таблицы
        """
        all_str = ("SELECT * FROM {}".format(table))
        self.cursor.execute(all_str)
        return self.cursor.fetchall()

    def rename_column(self, table, old_name, new_name, Type):
        """
        Автор:Сорокин Н.А
        Метод меняет название таблицы
        :param table:Имя таблици
        :param old_name:Старое имя столбца
        :param new_name:Новое имя столбцов
        :param Type:Тип данных
        :return:
        """
        # Проверяем тип переменной и переименовываем её
        if Type == 'str':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {} ".format(table, old_name, new_name, "VARCHAR(100)"))
        if Type == 'int':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {}".format(table, old_name, new_name, "INT"))
        if Type =='date':
            rename_stmt = ("ALTER TABLE {} CHANGE COLUMN {} {} {}".format(table, old_name, new_name, "DATE"))
        self.cursor.execute(rename_stmt)
        self.cnx.commit()

    def table_list(self, name, password, host):
        """
        Автор:Сорокин Н.А
        Выводит список баз данных
        :param name: Логин пользователя
        :param password: Пароль
        :param host: IP хоста
        :return:Возвращает список названий баз данных
        """
        self.get_connection(name, password, host)
        self.cursor.execute("SHOW DATABASES")
        lst = self.cursor.fetchall()
        new_lst = [value[0] for value in lst]# перезаписывем данные в список
        bases = []
        # Проверяем базы данных на наличие в них требуемых таблиц
        for base in new_lst:
            tables = self.Show_tables(base)
            if ("Books" in tables and "Readers" in tables and "Orders" in tables) or ("books" in tables and "readers" in tables and "orders" in tables):
                bases.append(base)
        return bases

    def Show_tables(self,bd):
        """
        Автор:Сорокин Н.А
        Метод возвращает список таблиц в базе данных
        :param bd: Имя базы данных
        :return: возвращает список таблиц
        """
        self.cursor.execute("SHOW TABLES FROM {}".format(bd))
        return [value[0] for value in self.cursor.fetchall()]

    def Del_db(self, db_name):
        """
        Автор:Сорокин Н.А
        Удаляет базу данных
        :param db_name:Имя базы данных
        :return:
        """
        del_stmt = "DROP DATABASE {}".format(db_name)
        self.cursor.execute(del_stmt)
        self.cnx.commit()

    def close_all(self):
        """
        Автор:Сорокин Н.А
        Метод отключает от MySql сервера
        :return:
        """
        if self.connected:
            self.cursor.close()
            self.cnx.close()
            self.connected = False

