from tkinter import *
from tkinter.simpledialog import  *
from PasswordDialog import MyDialog
from Skrolbar import ScrolledList
from AskDialog import AskNumber
from PIL.ImageTk import PhotoImage
from tkinter.filedialog import askopenfilename
import os
import datetime

class Search_dialog(Toplevel):
    def __init__(self, root, frame):
        super().__init__(root)
        self.root = root
        self.frame = frame
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w / 2.7), int(h / 2.7)))
        self.resizable(False, False)
        imgicon = PhotoImage(file=os.path.abspath(os.curdir)[:8] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)

        self.var = StringVar()
        Label(self, text="Select search criteria").pack()
        Radiobutton(self, text="Search by value in a field", variable=self.var, value="1").pack()
        Radiobutton(self, text="To withdraw readers who do have debts", variable=self.var, value="2").pack()
        Radiobutton(self, text="To withdraw readers who do not have debts", variable=self.var, value="3").pack()
        Checkbutton(self, text="Вывести среднее значение полей(при наличии) и их количество в таблицу",
                    command=(lambda i=0: self.onPress(i))).pack()
        Checkbutton(self, text="Вывести среднее значение полей(при наличии) и их количество в файл",
                    command=(lambda i=1: self.onPress(i))).pack()
        Button(self, text="OK", command=self.Check).pack()

        self.cols = []
        self.rows = []
        self.states = [False, False]
        self.count_rows = 0
        self.count = 0
        self.average = 0
        self.Table_name = ''

        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()

    def Check(self):
        pick = self.var.get()
        if self.frame.Lib.connected:
            if pick == "2":

                self.Table_name = "Orders"
                lst = self.frame.Lib.get_strings("Orders")
                new_lst = []
                for data in lst:
                    if str(datetime.date.today() - data[4])[0] == "-":
                        new_lst.append(data)
                new_lst.insert(0,tuple(("id," + self.frame.Lib.keys[self.Table_name][0][1:-1]).split(',')))
                self.frame.add_strs(new_lst)
            elif pick =="3":
                self.Table_name = "Orders"

                lst = self.frame.Lib.get_strings("Orders")
                new_lst = []
                for data in lst:
                    if str(datetime.date.today() - data[4])[0] != "-":
                        new_lst.append(data)
                new_lst.insert(0, tuple(("id," + self.frame.Lib.keys[self.Table_name][0][1:-1]).split(',')))
                self.frame.add_strs(new_lst)

                self.destroy()
            elif pick == "1":
                self.frame.Select_table(False)
                fields = list(("id," + self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(','))
                sc = ScrolledList(self.root, fields, self.Table_name, "selected field")
                field = sc.name
                n_field = fields.index(field)

                if self.frame.Types[self.frame.Table_name][n_field] == "int":
                    An = AskNumber(self.root, field)

                    lst = self.frame.Lib.get_strings(self.frame.Table_name)
                    new_lst = []
                    for data in lst:
                        if data[n_field] <= An.Upper_border and data[n_field] >= An.lower_bound :
                            self.count+=1
                            self.average += data[n_field]
                            new_lst.append(data)
                    self.average = self.average/self.count
                    new_lst.insert(0, tuple(("id," + self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(',')))
                    self.frame.add_strs(new_lst)

                    if self.states[0]:  # проверяем хочет ли пользователь вывести средние значение
                        self.frame.add_column("Средние значение", [self.average])
                        self.frame.add_column("Кол-во", [self.count])

                    if self.states[1]:
                        Path = askopenfilename(initialdir=os.path.abspath(os.curdir)[:8] + "Data",
                                               filetypes=[("Text files", ".txt"), ("CSV files", ".csv")])
                        with open(Path, "w") as f:
                            f.write("Average score {}, count {}".format(self.average, self.count))

                    self.destroy()

                elif self.frame.Types[self.frame.Table_name][n_field] == "str":
                    String = askstring('Library Base', "Enter string")

                    if String:
                        lst = self.frame.Lib.get_strings(self.frame.Table_name)
                        new_lst = []
                        for data in lst:
                            if data[n_field] == String:
                                new_lst.append(data)
                        new_lst.insert(0, tuple(("id," + self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(',')))
                        self.frame.add_strs(new_lst)

        else:
            self.dialog = MyDialog(self.root, self.frame.Lib)
            if self.frame.Lib.connected:
                self.frame.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1')
                Data = ''
                sc = ScrolledList(self.root, self.frame.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),Data, "selected table")
                self.Data_name = sc.name
                self.frame.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1', self.Data_name)


    def onPress(self,i): # сохраняет состояния
        self.states[i] = not self.states[i]

"""
    def Info_win(self):
        win = Toplevel(self.root)
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        win.geometry("+{}+{}".format(int(w / 2.2), int(h / 2.3)))
        win.resizable(False, False)
        imgicon = PhotoImage(file=os.path.abspath(os.curdir)[:8] + "Graphics\\" + "logo3.png")
        win.tk.call('wm', 'iconphoto', win._w, imgicon)

        Label(win, text = "Количество записей : {}".format(self.count)).pack()
        Label(win, text = "Среднее значение : {}".format(self.average)).pack()

        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()
"""