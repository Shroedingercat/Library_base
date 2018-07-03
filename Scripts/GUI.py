import sys
import os
Path = (os.path.abspath(os.curdir)).replace("\\", "/")
sys.path.append(Path[:Path.find("Scripts")] + "\\Library")

from tkinter import * # импортировать базовый набор виджетов
from tkinter.simpledialog import  * # импортировать стандартные диалоги
from PIL.ImageTk import PhotoImage
import PIL
from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.colorchooser import askcolor
from GuiWidgets import *
from Data import *
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import export_graphviz
from sklearn.tree import DecisionTreeClassifier
import os


class Main(Frame):
    """
    Автор:Сорокин Н.А
    Класс задаёт Frame главного окна
    """
    def __init__(self, root):
        """
        Автор:Сорокин Н.А
        Конструктор класса
        :param root: родительское окно
        """
        super().__init__(root)
        # Считываем размеры экрана задаём относительно их размеры окна
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry("{}x{}+{}+{}".format(w // 2, h // 2, w // 4, h // 4))
        Path = os.path.abspath(os.curdir).replace("\\", "/")# Находим путь до текущей директории
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics/" +"logo3.png")
        root.tk.call('wm', 'iconphoto', root._w, imgicon)# Размещаем иконку
        self.Lib = DataBase()
        self.makemenu()
        self.cols = []
        self.rows = []
        self.clf = None
        self.Table = None
        self.dialog = None
        self.s_dialog = None
        self.color = None
        self.fields = None
        self.Showed = False
        self.flag =True
        self.Strings = ''
        self.Table_name = ''
        self.Data_name = ''
        self.Types = {"Books":["int", "str", "str", "int","str"],
                      "Readers":["int", "str", "str", "int"],
                      "Orders":["int", "int", "int", "date", "date"]}

    def makemenu(self):
        """
        Автор:Сорокин Н.А
        Метод создаёт меню бар
        :return:
        """
        menubar = Frame(root,bd=2, relief=RAISED)
        menubar.pack(side=TOP, fill=X)

        self.fbutton = Menubutton(menubar,text = "Файл", underline=0)
        self.fbutton.pack(side=LEFT)
        self.file = Menu(self.fbutton)
        self.file.add_command(label="Новая база данных", command=self.new_data)
        self.file.add_command(label="Сохранить",command=self.Save)
        self.file.add_command(label="Выбрать базу данных", command=self.Select_base)
        self.file.add_command(label="Сохранить", command=self.Save)
        self.file.add_command(label="Выйти", command=self.Lib.close_all)
        self.fbutton.config(menu=self.file)

        self.tbutton = Menubutton(menubar, text = "Таблицы")
        self.tbutton.pack(side=LEFT)
        self.Tables = Menu(self.tbutton)
        self.Tables.add_command(label="Загрузить таблицу из файла", command=self.Load_data)
        self.Tables.add_command(label="Вывести таблицу", command=self.Select_table)
        self.Tables.add_command(label="Сохранить таблицу как...", command=self.Save_table)
        self.Tables.add_command(label="Поменять IP базы данных", command=self.Change_ip)
        self.tbutton.config(menu=self.Tables)

        self.Ibutton = Menubutton(menubar, text= "Интерфейс")
        self.Ibutton.pack(side=LEFT)
        self.Inter = Menu(self.Ibutton)
        self.Inter.add_command(label="Поменять размер шрифта", command = self.Change_font)
        self.Inter.add_command(label="Поменять цвет", command = self.Change_col)
        self.Ibutton.config(menu=self.Inter)

        self.Gbutton = Menubutton(menubar, text = "Графики")
        self.Gbutton.pack(side=LEFT)
        self.Grath = Menu(self.Gbutton)
        self.Grath.add_command(label="Показать график", command=self.Show_grath)
        self.Gbutton.config(menu = self.Grath)

        self.Mlbutton = Menubutton(menubar, text = "Анализ")
        self.Mlbutton.pack(side=LEFT)
        self.Ml = Menu(self.Mlbutton)
        self.Ml.add_command(label="Обучить дерево", command=self.learn)
        self.Ml.add_command(label="Определить самый важный признак", command=self.feature)
        self.Ml.add_command(label="Предсказание", command=self.Predict)
        self.Ml.add_command(label= "Сохранить алгоритм построения дерева в dot файл", command = self.Show_tree)
        self.Mlbutton.config(menu = self.Ml)

    def Change_ip(self):
        """
        Автор:Сорокин Н.А
        Меняет ip
        :return:
        """
        IP = askstring("Library base", "Введите ip")
        if self.Lib.connected:
            self.Lib.close_all()
            self.dialog.login = None
            self.dialog.password = None
        self.dialog = PasswordDialog(root, self.Lib, IP)

    def learn(self):
        """
        Автор:Сорокин Н.А
        Метод размечает данные и обучает дерево
        :return:
        """

        if self.Data_name:
            if self.Lib.get_strings("Books") and self.Lib.get_strings("Readers") and self.Lib.get_strings("Orders"):
                # Размечаем данные для таблицы Books
                data = self.Lib.get_strings("Books")
                books_names = []
                author = []
                years = []
                pablish = []
                Id = []
                self.all_cat = [Id,books_names, author,years, pablish]
                new_data_Books = []
                for i in range(len(data)):
                    new_col = []
                    for j in range(len(data[i])):
                        if j != 3 and j != 0:
                            if not data[i][j] in self.all_cat[j]:
                                self.all_cat[j].append(data[i][j])
                            new_col.append(self.all_cat[j].index(data[i][j]))
                        else:
                            new_col.append(int(data[i][j]))
                    new_data_Books.append(new_col)

                # Размечаем данные для таблицы Readers
                data = self.Lib.get_strings("Readers")
                ID = []
                names = []
                numbers = []
                years2 =  []
                self.all_cat2 = [ID, names, numbers, years2]
                new_data_Readers = []
                for i in range(len(data)):
                    new_col = []
                    for j in range(len(data[i])):
                        if j != 0 and j!= 3:
                            if not data[i][j] in self.all_cat2[j]:
                                self.all_cat2[j].append(data[i][j])
                            new_col.append(self.all_cat2[j].index(data[i][j]))
                        else:
                            new_col.append(int(data[i][j]))
                    new_data_Readers.append(new_col)

                # Объеденяем данные
                data = self.Lib.get_strings("Orders")
                Y = []
                X = []
                for dt in data:
                    if str(dt[4] - datetime.date.today())[0] == "-":
                        Y.append(1)
                    else:
                        Y.append(0)
                    X.append(new_data_Books[self.Fiend_id(dt[1], new_data_Books)][1:] +
                             new_data_Readers[self.Fiend_id(dt[2], new_data_Readers)][1:])

                Y = np.array(Y)
                X = np.array(X)
                #обучаем дерево
                self.clf = DecisionTreeClassifier(random_state=241)
                self.clf.fit(X, Y)
            else:
                showerror("Fail", "Не загружена одна из таблиц!")

        else:
            self.Select_base()
            if self.Data_name:
                self.learn()

    def feature(self):
        """
        Автор:Сорокин Н.А
        Метод выводит самый важный признак
        :return:
        """
        if self.clf:
            fet = ["name_book", "author", "year", "publishing_home", "name_reader", "telephone_number", "year_of_birth"]
            showinfo("Library base", "Самый важный признак для своевременного возврата книги:{}".format(fet[self.clf.feature_importances_.argmax()]))
        else:
            showwarning("Library base", "Сначало обучите дерево")

    def Predict(self):
        """
        Автор:Сорокин Н.А
        Метод выдаёт предсказание пользователю
        :return:
        """
        if self.clf:

            Ml_win = MlWindow(root)#Вызываем окно ввода данных
            #Проверяем введённые данные и класифицируем строковые типы
            if Ml_win.data[0] in self.all_cat[1]:
                Ml_win.data[0] = self.all_cat[1].index(Ml_win.data[0])
            else:
                Ml_win.data[0] = len(self.all_cat[1])-1

            if Ml_win.data[1] in self.all_cat[2]:
                Ml_win.data[1] = self.all_cat[2].index(Ml_win.data[1])
            else:
                Ml_win.data[1] = len(self.all_cat[2])-1

            if Ml_win.data[3] in self.all_cat[4]:
                Ml_win.data[3] = self.all_cat[4].index(Ml_win.data[3])
            else:
                Ml_win.data[3] = len(self.all_cat[4])-1

            if Ml_win.data[4] in self.all_cat2[1]:
                Ml_win.data[4] = self.all_cat2[1].index(Ml_win.data[4])
            else:
                Ml_win.data[4] = len(self.all_cat2[1])-1

            if Ml_win.data[5] in self.all_cat2[2]:
                Ml_win.data[5] = self.all_cat2[2].index(Ml_win.data[5])
            else:
                Ml_win.data[5] = len(self.all_cat2[2])-1

            Ml_win.data[2] = int(Ml_win.data[2])
            Ml_win.data[6] = int(Ml_win.data[6])
            junk = [[1,1,1,1,1,1,1],Ml_win.data]
            if self.clf.predict(np.array(junk))[1]:# Выводим предсказание
                showinfo("Library base","Читатель вернёт книгу")
            else:
                showinfo("Library base", "Читатель не вернёт книгу")
        else:
            showwarning("Library base", "Сначало обучите дерево")

    def Show_tree(self):
        """
        Автор:Сорокин Н.А
        Метод сохраняет dot файл с алгоритмом построения дерева
        :return:
        """
        if self.clf:
            Path = os.path.abspath(os.curdir)
            Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data") + ".dot"
            if Path:
                dot_data = export_graphviz(self.clf, out_file=Path, class_names=["Рassed", "not passed"],
                                 impurity=False, filled=True)
                showinfo("Library base", "Теперь вы можете отобразить дерево с помощью сайта http://www.webgraphviz.com/"
                                         "или с помощью подобных сайтов")
        else:
            showwarning("Library base", "Сначало обучите дерево")

    def Load_data(self):
        """
        Автор:Сорокин Н.А
        Метод загружает данные из файла
        :return:
        """
        if self.Data_name:# Проверяем была ли ранее выбрана база данных
            # Вызываем окно выбора таблицы
            Sc = ScrolledList(self, ("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
            self.Table_name = Sc.name
            Path = (os.path.abspath(os.curdir)).replace("\\", "/")# Находим путь до текущей директории
            Path = askopenfilename(initialdir = Path[:Path.find("Scripts")]+ "Data",
                                   filetypes=[("Text files",".txt"),("CSV files", ".csv")] )
            if Path != '':# проверяем выбрал ли пользователь файл
                Path = ("'" + Path + "'")
                self.Lib.load_data(Path, self.Table_name)
        else:
            self.Select_base()
            if self.Data_name:
                self.Load_data()

    def Change_font(self):
        """
        Автор:Сорокин Н.А
        Метод меняет размер шрифта главного окна
        :return:
        """
        size = askinteger("Library base", "Введите размер шрифта")
        if size:
            self.fbutton.config(font=size)
            self.tbutton.config(font=size)
            self.Ibutton.config(font=size)
            self.Gbutton.config(font=size)
            self.file.config(font=size)
            self.Inter.config(font=size)
            self.Tables.config(font=size)
            self.Grath.config(font=size)

    def Change_col(self):
        """
        Автор:Сорокин Н.А
        Меняет здний фон главного окна
        :return:
        """
        self.color = askcolor()
        if self.color:
            root.config(bg = self.color[1])
            toolbar.config(bg = self.color[1])


    def Save(self):
        """
        Автор:Сорокин Н.А
        Метод сохраняет изменения в таблице
        :return:
        """
        if self.Table:# Проверяем была ли ранее выбрана таблица
            if self.Lib.connected:
                self.fields = tuple((self.Lib.keys[self.Table_name][0][1:-1]).split(','))
                self.Strings = [self.fields] + self.Lib.get_strings(self.Table_name)# Считываем последние данные из базы

                for i in range(len(self.Types[self.Table_name])): #Проверяем и меняем названия столбцов
                    data = self.Table.rows[0][i].get()
                    if data != self.Strings[0][i]:
                        if i !=0:
                            self.Lib.rename_column(self.Table_name, self.Strings[0][i],
                                                data, self.Types[self.Table_name][i])
                        else:
                            showwarning("warning", "Поле ID нельзя изменить!")

                for i in range(1,len(self.Table.rows)):# Проверяем и меняем значения остальных полей таблиц
                    String = []
                    flag = True
                    for j in range(len(self.Types[self.Table_name])):
                        data = self.Table.rows[i][j].get()
                        if self.Types[self.Table_name][j] == "int":
                            try:# Проверяем коректность введенных данных
                                data = int(data)
                            except:
                                showerror("Fail",
                                        "Не корректный формат ввода {} строка, {} столбец".format(i,j+1))
                                flag = False
                        if self.Types[self.Table_name][j] == "data":
                            try:# Проверяем корректность введенных данных
                                data = datetime.date(data)
                            except:
                                showerror("Fail",
                                        "Не корректный формат ввода {} строка, {} столбец".format(i,j+1))
                                flag = False
                        String.append(data)
                        if i < len(self.Strings) - 1:
                            if data != self.Strings[self.Fiend_id(int(self.Table.rows[i][0].get()),self.Strings)][j] and j != 0 and flag:
                                self.Lib.Change_data(self.Table_name, self.fields[j],
                                                    self.Table.rows[i][0].get(), data,self.Types[self.Table_name][j])

                    if i > len(self.Strings) - 1 and flag:# проверяем добавил ли пользователь новую строку
                            self.Lib.add_string(self.Table_name, String)

                showwarning("Saved", "Изменения были сохранены!")
        else:
            showwarning("warning", "Ни одна таблица не выбрана!")

    def Fiend_id(self, id, data, column = 0):
        """
        Автор:Сорокин Н.А
        Метод находит id в данных data
        :param id: id, который нужно найти
        :param data:данные в которых производится поиск
        :param column: столбец в котором производится поиск
        :return:i-номер искомых данных
        """
        for i in range(len(data)):
            if data[i][column] == id:
                return i

    def Select_base(self):
        """
        Автор:Сорокин Н.А
        Метод реализует выбор базы данных
        :return:
        """
        if self.Lib.connected:
            # Вызываем окно выбора бызы данных
            sc = ScrolledList(root, self.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),
                              self.Data_name, "Выберите базу данных")
            self.Data_name = sc.name
            if self.Data_name != '':# Проверяем был ли сделан пользователем выбор
                try:
                    self.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1', self.Data_name)
                except:
                    self.Data_name = ''
                    showerror("Fail", "Базы данных не существует!")
        else:
            self.dialog = PasswordDialog(root, self.Lib, '127.0.0.1')
            if self.Lib.connected:
                self.Select_base()

    def Select_table(self, flag = True):
        """
        Автор:Сорокин Н.А
        Метод реализует выбор таблици
        :param flag: параметр отвечающий за вывод таблици на экран
        :return:
        """
        if self.Lib.connected:# Проверяем подключение к базе данных
            if self.Data_name != '':
                sc = ScrolledList(root,("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
                self.Table_name = sc.name
                if flag:
                    self.Show_table()
            else:
                self.Select_base()
                self.Select_table()
        else:
            self.dialog = PasswordDialog(root, self.Lib, '127.0.0.1')# Вызываем окно ввода логина и пароля
            if self.Lib.connected:
                self.Select_base()
                if  self.Data_name != '':
                    self.Select_table()

    def Show_table(self):
        """
        Автор:Сорокин Н.А
        Выводит таблицу на экран
        :return:
        """
        if self.Table:
            self.Table.Destroy_table()# Если таблица уже выведена на экран, то уничтожаем ее
        self.max_rows = self.Lib.Max(self.Table_name) + 1
        if self.max_rows:
            self.max_cols = self.Lib.keys[self.Table_name][1].count('%s')
            self.fields = tuple((self.Lib.keys[self.Table_name][0][1:-1]).split(','))
            self.Strings =[self.fields]+self.Lib.get_strings(self.Table_name)# Получаем все данные из базы данных
            self.max_rows = len(self.Strings)
            if self.flag:
                self.Table = Table(root,self.color[1])
            self.Table.populate(self.max_cols, self.max_rows, self.Strings)# Вызавем метод создающий  заполняющий таблицу
            if self.flag:
                self.Table.pack(side="top", fill="both")
                self.flag = False


            self.Showed = True

    def new_data(self):
        """
        Автор:Сорокин Н.А
        Метод создаёт новую базу данных
        :return:
        """
        if self.Lib.connected:# Проверяем подключение к базе данных
            self.Data_name = ''
            self.Data_name = askstring("Library Base", "Введите название базы данных")
            if self.Data_name != '':# Проверяем ввел ли пользователь имя для базы данных
                self.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1')
                replied = self.Lib.check_database(self.Data_name)
                if not replied[0]:
                    showerror("Fail",replied[1])
                self.Lib.create_tables()
                self.Lib.create_tables()
        else:
            self.dialog = PasswordDialog(root, self.Lib, '127.0.0.1')# Вызываем окно ввода логина и пароля
            if self.Lib.connected:
                self.new_data()

    def Search(self):
        """
        Автор:Сорокин Н.А
        Метод вызывает окно поиска
        :return:
        """
        if self.Table:
            self.Table.destroy()# Если таблица уже выведена на экран, то уничтожаем ее
        if self.flag:
            self.Table = Table(root,self.color[1])
        Search_dialog(root, self)
        if self.flag:
            self.Table.pack(side="top", fill="both")
            self.flag = False

    def add_str(self):
        """
        Автор:Сорокин Н.А
        Метод добавляет новую строку
        :return:
        """
        if self.Table:
            column = len(self.Types[self.Table_name])
            self.Table.add_str(column)
        else:
            showwarning("warning", "Не одна таблица не выбрана!")

    def Del_str(self):
        """
        Метод удаляет строку или строки
        :return:
        """
        if self.Table_name:
            askN = AskNumber(root, "id")# вызываем окно ввода двух значений
            if askN.lower_bound and askN.Upper_border:
                for ID in range(int(askN.lower_bound), int(askN.Upper_border)+1):
                    self.fields = tuple((self.Lib.keys[self.Table_name][0][1:-1]).split(','))
                    self.Strings = [self.fields] + self.Lib.get_strings(self.Table_name)# Получаем все данные из базы данных
                    self.Lib.DEL(self.Table_name, ID)
                    index = self.Fiend_id(ID, self.Strings)
                    if index:
                        for ent in self.Table.rows[index]:
                            ent.destroy()
                        del self.Table.rows[index]
            showwarning("warning", "Данные успешно удалены!")
        else:
            showwarning("warning", "Не одна таблица не выбрана!")

    def Show_grath(self):
        """
        Автор:Сорокин Н.А
        Метод реализует построение и отображение графика
        :return:
        """
        if self.Data_name != '':# Проверяем была ли ранее выбрана база данных
            lst = self.Lib.get_strings("Orders")
            lst_readers = self.Lib.get_strings("Readers")
            times = []
            years = []
            for time in lst:# проверяем кол-во дней оставшихся до сдачи книги
                times.append((time[4]-datetime.date.today()).days)
                years.append(lst_readers[self.Fiend_id(time[2], lst_readers)][3])
            line =  plt.plot(times, years, 'o')
            plt.title(u"Зависимость года рождения, от времени оставшемся до сдачи книги")
            plt.xlabel(u'Время оставшиеся до сдачи книги')
            plt.ylabel(u'Год рождения')
            plt.grid()
            plt.show()

        else:
            self.Select_base()
            if self.Data_name != '':
                self.Show_grath()

    def del_database(self):
        """
        Автор:Сорокин Н.А
        Метод удаляет базу данных
        :return:
        """
        if self.Lib.connected:
            sc = ScrolledList(root, self.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),
                              self.Data_name, "Выберите базу данных")
            if sc.name != '':
                self.Lib.Del_db(sc.name)
                showwarning("warning", "База данных удалена!")
        else:
            self.dialog = PasswordDialog(root, self.Lib, '127.0.0.1')
            if self.Lib.connected:
                self.del_database()

    def Save_table(self):
        """
        Автор:Сорокин Н.А
        Метод сохраняет таблицу в файл
        :return:
        """
        if self.Data_name != '':
            #вызываем окно выбора таблицы
            sc = ScrolledList(root, ("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
            Path = os.path.abspath(os.curdir)
            Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data",
                                     filetypes=[("Text files", ".txt"), ("CSV files", ".csv")])
            if os.path.exists(Path):
                os.remove(Path)#Удаляем файл если он уже есть
            if sc.name and Path:
                self.Lib.save_data("'{}'".format(Path), sc.name)
        else:
            self.Select_base()
            self.Save_table()



if __name__ == '__main__':
    root = Tk()     #Создаём родительское окно
    app = Main(root)
    app.pack()

    Path = os.path.abspath(os.curdir).replace("\\", "/")   #Считываем путь до текущей дериктории

    toolbar = Frame(root,relief = SUNKEN)   #Создаём Toolbar
    toolbar.pack(side="top", fill="both")
    # Дальше создаем кнопки и помещаем в них картинки, предварительно поменяв их размер
    imgobj = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/"  + "disketa2.png")
    imgobj.thumbnail((40, 40), PIL.Image.ANTIALIAS)
    img = PhotoImage(imgobj)
    btn_save = Button(toolbar, image=img, command= app.Save)
    btn_save.config(width=40, height=40)
    btn_save.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_save, "Сохранить таблицу")

    imgobj2 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "rules.png")
    imgobj2.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img2 = PhotoImage(imgobj2)
    btn_load = Button(toolbar, image=img2, command=app.Select_table)
    btn_load.config(width=40,height=40)
    btn_load.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_load, "Вывести таблицу")

    imgobj8 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "delete-database.png")
    imgobj8.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img8 = PhotoImage(imgobj8)
    btn_DelBd = Button(toolbar, image=img8, command=app.del_database)
    btn_DelBd.config(width=40, height=40)
    btn_DelBd.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_DelBd, "Удалить базу данных")

    imgobj3 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "new-database.png")
    imgobj3.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img3 = PhotoImage(imgobj3)
    btn_new = Button(toolbar, image=img3, command=app.new_data)
    btn_new.config(width=40, height=40)
    btn_new.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_new, "Создать базу данных")

    imgobj4 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "Search.png")
    imgobj4.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img4 = PhotoImage(imgobj4)
    btn_search = Button(toolbar, image=img4, command=app.Search)
    btn_search.config(width=40, height=40)
    btn_search.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_search, "Искать")

    imgobj7 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "add3.png")
    imgobj7.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img7 = PhotoImage(imgobj7)
    btn_add = Button(toolbar, image=img7, command=app.add_str)
    btn_add.config(width=40, height=40)
    btn_add.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_add, "Добавить строку")

    imgobj5 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" +"Del3.png")
    imgobj5.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img5 = PhotoImage(imgobj5)
    btn_Del = Button(toolbar, image=img5, command=app.Del_str)
    btn_Del.config(width=40, height=40)
    btn_Del.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_Del, "Удалить строки")

    imgobj6 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics/" + "delete_user.png")
    imgobj6.thumbnail((40,40), PIL.Image.ANTIALIAS)
    img6 = PhotoImage(imgobj6)
    btn_exit = Button(toolbar, image=img6, command=app.Lib.close_all)
    btn_exit.config(width=40, height=40)
    btn_exit.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_exit, "Выйти")

    root.title('Library Base')
    root.mainloop()
