import sys
sys.path.insert(0, 'C:/Work/Library_base/Library')
from tkinter import * # импортировать базовый набор виджетов
from tkinter.simpledialog import  * # импортировать стандартные диалоги
from PIL.ImageTk import PhotoImage
import PIL
from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from scipy import interpolate
from GuiWidgets import *
from Data import DataBase
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

class Main(Frame):
    def __init__(self, root):
        super().__init__(root)
        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry("{}x{}+{}+{}".format(w // 2, h // 2, w // 4, h // 4))
        Path = os.path.abspath(os.curdir)
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics\\" +"logo3.png")
        root.tk.call('wm', 'iconphoto', root._w, imgicon)
        self.Lib = DataBase()
        self.makemenu()
        self.cols = []
        self.rows = []
        self.Table = None
        self.dialog = None
        self.Showed = False
        self.flag =True
        self.Strings = ''
        self.Table_name = ''
        self.Data_name = ''
        self.Types = {"Books":["int", "str", "str", "int","str"],
                      "Readers":["int", "str", "str", "int"],
                      "Orders":["int", "int", "int", "date", "date"]}

    def makemenu(self):
        top = Menu(root)
        root.config(menu=top)

        file = Menu(top)
        file.add_command(label="Новая база данных", command=self.new_data)
        file.add_command(label="Сохранить",command=self.Save)
        file.add_command(label="Выбрать базу данных", command=self.Select_base)
        file.add_command(label="Сохранить", command=self.Save)
        file.add_command(label="Выйти", command=self.Lib.close_all)
        top.add_cascade(label="Файл", menu = file)

        Tables = Menu(top)
        Tables.add_command(label="Загрузить таблицу из файла", command=self.Load_data)
        Tables.add_command(label="Вывести таблицу", command=self.Select_table)
        Tables.add_command(label="Сохранить таблицу как...", command=self.Save_table)

        top.add_cascade(label="Таблицы", menu=Tables)

        Grath = Menu(top)
        Grath.add_command(label="Показать график", command=self.Show_grath)
        top.add_cascade(label="Графики", menu=Grath)

    def Load_data(self):
        if self.Data_name:
            Sc = ScrolledList(self, ("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
            self.Table_name = Sc.name
            Path = askopenfilename(initialdir = os.path.abspath(os.curdir)[:8] + "Data",
                                   filetypes=[("Text files",".txt"),("CSV files", ".csv")] )
            Path = ("'" + Path + "'")
            if Path != '':
                self.Lib.load_data(Path, self.Table_name)
        elif not self.Lib.connected:
            self.dialog = PasswordDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()
                self.Load_data()
        else:
            self.Select_base()
            self.Load_data()

    def Save(self):
        if self.Table:
            if self.Lib.connected:
                self.fields = tuple((self.Lib.keys[self.Table_name][0][1:-1]).split(','))
                self.Strings = [self.fields] + self.Lib.get_strings(self.Table_name)

                for i in range(len(self.Types[self.Table_name])): #Проверяем и меняем названия столбцов
                    flag = True
                    data = self.Table.rows[0][i].get()
                    if data != self.Strings[0][i]:
                        self.Lib.rename_column(self.Table_name, self.Strings[0][i], data, self.Types[self.Table_name][i])

                for i in range(1,len(self.Table.rows)):
                    String = []
                    for j in range(len(self.Types[self.Table_name])):
                        data = self.Table.rows[i][j].get()
                        if self.Types[self.Table_name][j] == "int":
                            try:
                                data = int(data)
                            except:
                                showerror("Fail",
                                        "Не верный формат ввода {} строка, {} столбец".format(i,j+1))
                                flag = False
                                break
                        if self.Types[self.Table_name][j] == "data":
                            try:
                                data = datetime.date(data)
                            except:
                                showerror("Fail",
                                        "Не верный формат ввода {} строка, {} столбец".format(i,j+1))
                                flag = False
                                break
                        String.append(data)
                        if i < len(self.Strings) - 1:
                            if data != self.Strings[self.Fiend_id(int(self.Table.rows[i][0].get()),self.Strings)][j] and j != 0:
                                self.Lib.Change_data(self.Table_name, self.fields[j],
                                                    self.Table.rows[i][0].get(), data,self.Types[self.Table_name][j])

                    if i > len(self.Strings) - 1 and flag:
                            self.Lib.add_string(self.Table_name, String)

                showwarning("Saved", "Изменения были сохранены!")
            else:
                showwarning("warning", "Ни одна таблица не выбрана!")

    def Fiend_id(self, id, data, column = 0):
        for i in range(len(data)):
            if data[i][column] == id:
                return i

    def Select_base(self):
        if self.Lib.connected:
            sc = ScrolledList(root, self.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),
                              self.Data_name, "Выберите базу данных")
            self.Data_name = sc.name
            if self.Data_name != '':
                try:
                    self.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1', self.Data_name)
                except:
                    self.Data_name = ''
                    showerror("Fail", "The database does not exist")
        else:
            self.dialog = PasswordDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()

    def Select_table(self, flag = True):
        if self.Lib.connected:
            if self.Data_name != '':
                sc = ScrolledList(root,("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
                self.Table_name = sc.name
                if flag:
                    self.Show_table()
            else:
                self.Select_base()
                self.Select_table()
        else:
            self.dialog = PasswordDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()
                if  self.Data_name != '':
                    self.Select_table()

    def Show_table(self):
        if self.Table:
            self.Table.Destroy_table()
        self.max_rows = self.Lib.Max(self.Table_name) +1
        if self.max_rows:
            self.max_cols = self.Lib.keys[self.Table_name][1].count('%s')
            self.fields = tuple((self.Lib.keys[self.Table_name][0][1:-1]).split(','))
            self.Strings =[self.fields]+self.Lib.get_strings(self.Table_name)
            self.max_rows = len(self.Strings)
            if self.flag:
                self.Table = Table(root)
            self.Table.populate(self.max_cols, self.max_rows, self.Strings)
            if self.flag:
                self.Table.pack(side="top", fill="both")
                self.flag = False


            self.Showed = True

    def new_data(self):
        if self.Lib.connected:
            self.Data_name = ''
            self.Data_name = askstring("Library Base", "Input Database name")
            if self.Data_name != '':
                self.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1')
                replied = self.Lib.check_database(self.Data_name)
                if not replied[0]:
                    showerror("Fail",replied[1])
                self.Lib.create_tables()
                self.Lib.create_tables()
        else:
            self.dialog = PasswordDialog(root, self.Lib)
            if self.Lib.connected:
                self.new_data()

    def Search(self):
        if self.Table:
            self.Table.destroy()
        if self.flag:
            self.Table = Table(root)
        Search_dialog(root, self)
        if self.flag:
            self.Table.pack(side="top", fill="both")
            self.flag = False

    def add_str(self):
        if self.Table:
            column = len(self.Types[self.Table_name])
            self.Table.add_str(column)
        else:
            showwarning("warning", "Не одна таблица не выбрана!")

    def Del_str(self):
        if self.Table_name:
            askN = AskNumber(root, "id")
            for ID in range(int(askN.lower_bound), int(askN.Upper_border)+1):
                self.Strings = [self.fields] + self.Lib.get_strings(self.Table_name)
                self.Lib.DEL(self.Table_name, ID)
                index = self.Fiend_id(ID, self.Strings)
                if index:
                    for ent in self.Table.rows[index]:
                        ent.destroy()
                    del self.Table.rows[index]
        else:
            showwarning("warning", "Не одна таблица не выбрана!")

    def Show_grath(self):
        if self.Data_name != '':
            lst = self.Lib.get_strings("Orders")
            lst_readers = self.Lib.get_strings("Readers")
            times = []
            years = []
            for time in lst:
                times.append((time[4]-datetime.date.today()).days)
                years.append(lst_readers[self.Fiend_id(time[2], lst_readers)][3])
            line =  plt.plot(times, years, 'o')
            plt.title(u"Зависимость года рождения от времени оставшемся до сдачи книги")
            plt.xlabel(u'Время оставшиеся до сдачи книги')
            plt.ylabel(u'Год рождения')
            plt.grid()
            plt.show()

        else:
            self.Select_base()
            if self.Data_name != '':
                self.Show_grath()

    def del_database(self):
        if self.Lib.connected:
            sc = ScrolledList(root, self.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),
                              self.Data_name, "Выберите базу данных")
            if sc.name != '':
                self.Lib.Del_db(sc.name)
                showwarning("warning", "База данных удалена!")
        else:
            self.dialog = PasswordDialog(root, self.Lib)
            if self.Lib.connected:
                self.del_database()

    def Save_table(self):
        if self.Data_name != '':
            sc = ScrolledList(root, ("Books", "Readers", "Orders"), self.Table_name, "Выберите таблицу")
            Path = os.path.abspath(os.curdir)
            Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data",
                                     filetypes=[("Text files", ".txt"), ("CSV files", ".csv")])
            if os.path.exists(Path):
                os.remove(Path)
            if sc.name and Path:
                self.Lib.save_data("'{}'".format(Path), sc.name)
        else:
            self.Select_base()
            self.Save_table()



if __name__ == '__main__':
    root = Tk()
    app = Main(root)
    app.pack()

    Path = os.path.abspath(os.curdir)

    toolbar = Frame(root,relief = SUNKEN)
    toolbar.pack(side="top", fill="both")

    imgobj = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\"  + "diskette.jpg")
    img = PhotoImage(imgobj)
    btn_save = Button(toolbar, image=img, command= app.Save)
    btn_save.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_save, "Сохранить таблицу")

    imgobj2 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "rules.png")
    imgobj2.thumbnail((32,32), PIL.Image.ANTIALIAS)
    img2 = PhotoImage(imgobj2)
    btn_load = Button(toolbar, image=img2, command=app.Select_table)
    btn_load.config(width=32,height=32)
    btn_load.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_load, "Вывести таблицу")

    imgobj8 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "delete-database.png")
    imgobj8.thumbnail((32, 32), PIL.Image.ANTIALIAS)
    img8 = PhotoImage(imgobj8)
    btn_DelBd = Button(toolbar, image=img8, command=app.del_database)
    btn_DelBd.config(width=32, height=32)
    btn_DelBd.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_DelBd, "Удалить базу данных")

    imgobj3 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "new-database.png")
    imgobj3.thumbnail((32, 32), PIL.Image.ANTIALIAS)
    img3 = PhotoImage(imgobj3)
    btn_new = Button(toolbar, image=img3, command=app.new_data)
    btn_new.config(width=32, height=32)
    btn_new.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_new, "Создать базу данных")

    imgobj4 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "Search.png")
    imgobj4.thumbnail((32, 32), PIL.Image.ANTIALIAS)
    img4 = PhotoImage(imgobj4)
    btn_search = Button(toolbar, image=img4, command=app.Search)
    btn_search.config(width=32, height=32)
    btn_search.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_search, "Искать")

    imgobj7 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "add2.png")
    imgobj7.thumbnail((36, 32), PIL.Image.ANTIALIAS)
    img7 = PhotoImage(imgobj7)
    btn_add = Button(toolbar, image=img7, command=app.add_str)
    btn_add.config(width=32, height=32)
    btn_add.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_add, "Добавить строку")

    imgobj5 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" +"Del2.png")
    imgobj5.thumbnail((32, 32), PIL.Image.ANTIALIAS)
    img5 = PhotoImage(imgobj5)
    btn_Del = Button(toolbar, image=img5, command=app.Del_str)
    btn_Del.config(width=32, height=32)
    btn_Del.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_Del, "Удалить строки")

    imgobj6 = PIL.Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "user-blue-delete.png")
    imgobj6.thumbnail((32, 32), PIL.Image.ANTIALIAS)
    img6 = PhotoImage(imgobj6)
    btn_exit = Button(toolbar, image=img6, command=app.Lib.close_all)
    btn_exit.config(width=32, height=32)
    btn_exit.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_exit, "Выйти")



    root.title('Library Base')
    root.mainloop()
