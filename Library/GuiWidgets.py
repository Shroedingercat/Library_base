from tkinter import *
from tkinter.messagebox import *
from tkinter.simpledialog import  *
from PIL.ImageTk import PhotoImage
from tkinter.filedialog import asksaveasfilename
import os
import datetime
import os

class PasswordDialog(Toplevel):
    def __init__(self,root,Lib):
        super().__init__(root)
        self.Lib = Lib
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w/2.2),int(h/2.3)))
        self.resizable(False, False)
        Path = os.path.abspath(os.curdir)
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)
        Label(self, text="Введите логин и пароль:", font="Georgia 8").grid(row=0, column=2)
        Label(self, text="Логин:", font="Georgia 8").grid(row =1, column=1)
        Label(self, text="Пароль:", font="Georgia 8").grid(row=2, column=1)
        self.ent_login = Entry(self)
        self.ent_login.grid(row=1, column=2)
        self.ent_password= Entry(self, show="*")
        self.ent_password.grid(row=2, column=2)
        btn = Button(self, text="Готово", command=self.Check, font="Georgia 8")
        btn.grid(row=3, column=2)
        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()


    def Check(self):
        self.login = self.ent_login.get()
        self.password = self.ent_password.get()
        try:
            self.Lib.get_connection(self.login, self.password, '127.0.0.1')
            self.destroy()
        except:
            showwarning("Ok", "Wrong login or password")


class Search_dialog(Toplevel):
    def __init__(self, root, frame):
        super().__init__(root)
        self.root = root
        self.frame = frame
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w / 2.7), int(h / 2.7)))
        self.resizable(False, False)
        Path = os.path.abspath(os.curdir)
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)

        self.var = StringVar()
        Label(self, text="Выберите критерий поиска").pack()
        Radiobutton(self, text="Искать по значению в таблице", variable=self.var, value="1").pack()
        Radiobutton(self, text="Вывести читателей имеющих задолжности", variable=self.var, value="2").pack()
        Radiobutton(self, text="Вывести читателей не имеющих задолжностей", variable=self.var, value="3").pack()
        self.var.set("1")
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
                    if str(data[4] - datetime.date.today())[0] == "-":
                        self.count+=1
                        new_lst.append(data)
                new_lst.insert(0,tuple((self.frame.Lib.keys[self.Table_name][0][1:-1]).split(',')))
                self.frame.Table.add_strs(new_lst)
                if self.states[0]:
                    self.frame.Table.add_column("Кол-во", [self.count])
                if self.states[1]:
                    Path = os.path.abspath(os.curdir)
                    Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data",
                                           filetypes=[("Text files", ".txt")])
                    with open(Path, "w") as f:
                        f.write("count {}".format(self.count))

                self.destroy()

            elif pick =="3":
                self.Table_name = "Orders"

                lst = self.frame.Lib.get_strings("Orders")
                new_lst = []
                for data in lst:
                    if str(data[4] - datetime.date.today() )[0] != "-":
                        new_lst.append(data)
                new_lst.insert(0, tuple((self.frame.Lib.keys[self.Table_name][0][1:-1]).split(',')))
                self.frame.Table.add_strs(new_lst)

                self.destroy()
            elif pick == "1":
                self.frame.Select_table(False)
                fields = list((self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(','))
                sc = ScrolledList(self.root, fields, self.Table_name, "selected field")
                field = sc.name
                n_field = fields.index(field)

                if self.frame.Types[self.frame.Table_name][n_field] == "int":
                    An = AskNumber(self.root, field)
                    if An.Upper_border and An.lower_bound:
                        lst = self.frame.Lib.get_strings(self.frame.Table_name)
                        new_lst = []
                        for data in lst:
                            if data[n_field] <= An.Upper_border and data[n_field] >= An.lower_bound :
                                self.count+=1
                                self.average += data[n_field]
                                new_lst.append(data)
                        self.average = self.average/self.count
                        new_lst.insert(0, tuple(("id," + self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(',')))
                        self.frame.Table.add_strs(new_lst)

                        if self.states[0]:  # проверяем хочет ли пользователь вывести средние значение
                            self.frame.Table.add_column("Средние значение", [self.average])
                            self.frame.Table.add_column("Кол-во", [self.count])

                        if self.states[1]:
                            Path = os.path.abspath(os.curdir)
                            Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data",
                                                   filetypes=[("Text files", ".txt")])
                            with open(Path, "w") as f:
                                f.write("Average score {}, count {}".format(self.average, self.count))

                        self.destroy()

                elif self.frame.Types[self.frame.Table_name][n_field] == "str":
                    String = askstring('Library Base', "Enter string")

                    if String:
                        lst = self.frame.Lib.get_strings(self.frame.Table_name)
                        new_lst = []
                        for data in lst:
                            if  String in data[n_field]:
                                new_lst.append(data)
                                self.count+=1
                        new_lst.insert(0, tuple((self.frame.Lib.keys[self.frame.Table_name][0][1:-1]).split(',')))
                        self.frame.Table.add_strs(new_lst)
                        if self.states[0]:
                            self.frame.Table.add_column("Кол-во", [self.count])
                        if self.states[1]:
                            Path = os.path.abspath(os.curdir)
                            Path = asksaveasfilename(initialdir=Path[:Path.find("Scripts")] + "Data",
                                                     filetypes=[("Text files", ".txt")])
                            with open(Path, "w") as f:
                                f.write("count {}".format(self.count))

        else:
            self.dialog = PasswordDialog(self.root, self.frame.Lib)
            if self.frame.Lib.connected:
                self.frame.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1')
                Data = ''
                sc = ScrolledList(self.root, self.frame.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'),Data, "selected table")
                self.frame.Data_name = sc.name
                self.frame.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1', self.frame.Data_name)


    def onPress(self,i): # сохраняет состояния
        self.states[i] = not self.states[i]


class ScrolledList(Toplevel):
    def __init__(self,root, options, name, Text):
        super().__init__(root)
        self.name = name  # запретить доступ к др. окнам, пока открыт диалог
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w / 2.2), int(h / 2.3)))
        Path = os.path.abspath(os.curdir)
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)
        Label(self,text=Text, font= "Georgia 8").pack()
        self.makeWidgets(options)
        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()

    def handleList(self, event):
        index = self.listbox.curselection()  # при двойном щелчке на списке

        label = self.listbox.get(index)  # извлечь выбранный текст
        self.runCommand(label)  # и вызвать действие

        # или get(ACTIVE)
    def makeWidgets(self, options):
        sbar = Scrollbar(self)

        list = Listbox(self, relief=SUNKEN)
        sbar.config(command=list.yview)  # связать sbar и list
        list.config(yscrollcommand=sbar.set)  # сдвиг одного = сдвиг другого
        sbar.pack(side=RIGHT, fill=Y)  # первым добавлен – посл. обрезан
        list.pack(side=LEFT, expand=YES, fill=BOTH)  # список обрезается первым
        pos = 0
        for label in options:  # добавить в виджет списка
            list.insert(pos, label)  # или insert(END,label)
            pos += 1  # или enumerate(options)
        # list.config(selectmode=SINGLE, setgrid=1) # режимы выбора, измен. разм.
        list.bind('<Double-1>', self.handleList)  # установить обр-к события
        self.listbox = list

    def runCommand(self, selection):  # необходимо переопределить
        self.name = selection
        self.destroy()


class AskNumber(Toplevel):
    def __init__(self, root, field):
        super().__init__(root)
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w / 2.2), int(h / 2.3)))
        self.resizable(False, False)

        Label(self, text="Enter the border").grid(row=0, column=1)
        Label(self, text= "{} >=".format(field)).grid(row = 1, column=0)
        self.ent = Entry(self)
        self.ent.grid(row=1, column=1)
        Label(self, text="{} <=".format(field)).grid(row=2, column=0)
        self.ent2 = Entry(self)
        self.ent2.grid(row=2, column=1)
        Button(self, text="OK", command=self.read).grid(row=3, column=1)

        self.lower_bound = None
        self.Upper_border = None

        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()

    def read(self):
        try:
            self.lower_bound = float(self.ent.get())
            self.Upper_border = float(self.ent2.get())
        except:
            showerror("Fail", "Не верный формат ввода, повторите ещё раз!")


        self.destroy()


class Table(Frame):
    def __init__(self, root):

        Frame.__init__(self, root)
        self.rows = []
        self.canvas = Canvas(root)
        self.frame = Frame(self.canvas)
        self.vsb = Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)


    def populate(self, max_col, max_row, data):
        '''Put in some fake data'''
        self.max_col = max_col
        self.max_row = max_row
        self.data = data
        self.rows = []
        for i in range(self.max_row):
            self.cols = []
            for j in range(self.max_col):
                ent = Entry(self.frame,relief=RIDGE)
                ent.grid(row=i+1, column=j, sticky=NSEW)
                ent.insert(END,self.data[i][j])
                self.cols.append(ent)
            self.rows.append(self.cols)

    def add_column(self, column_name, Data = None):
        ent = Entry(self.frame, relief=RIDGE)
        ent.grid(row=1, column=len(self.rows[0]), sticky=NSEW)
        ent.insert(END, column_name)
        self.rows[0].append(ent)
        if len(Data) <= len(self.rows):
            if Data and len(self.rows)>1:
                for i in range(len(Data)):
                    ent = Entry(self.frame, relief=RIDGE)
                    ent.grid(row=i + 2, column=len(self.rows[0]) - 1, sticky=NSEW)
                    ent.insert(END, Data[i])
                    self.rows[i + 1].append(ent)


    def add_strs(self, data):
        if self.rows:
            self.Destroy_table()
        self.populate(len(data[0]), len(data), data)

    def add_str(self, column_len):
        cols = []
        for i in range(column_len):
            ent = Entry(self.frame, relief=RIDGE)
            ent.grid(row=len(self.rows)+1, column=i, sticky=NSEW)
            cols.append(ent)
        self.rows.append(cols)

    def Destroy_table(self):
        for lst in self.rows:
            for ent in lst:
                ent.destroy()
        self.rows = []

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


import tkinter as tk
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()