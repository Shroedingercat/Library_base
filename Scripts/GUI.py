from tkinter import * # импортировать базовый набор виджетов
from tkinter.simpledialog import  * # импортировать стандартные диалоги
from PIL.ImageTk import PhotoImage, Image
from tkinter.messagebox import *
from tkinter.filedialog import askopenfilename
from ToolTip import CreateToolTip
from PasswordDialog import MyDialog
from Data import DataBase
from Skrolbar import ScrolledList
from SearchDialog import Search_dialog
import datetime
import os

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
        self.Table_name = ''
        self.Data_name = ''
        self.dialog = None
        self.cols = []
        self.rows = []
        self.Showed = False
        self.Strings = ''
        self.Types = {"Books":["int", "str", "str", "int","str"],
                      "Readers":["int", "str", "str", "int"],
                      "Orders":["int", "int", "int", "date", "date"]}

    def makemenu(self):
        top = Menu(root)
        root.config(menu=top)

        file = Menu(top)
        file.add_command(label="New DataBase", command=self.new_data)
        file.add_command(label="Save",command=self.Save)
        file.add_command(label="Load table from file",command=self.Load_data)
        top.add_cascade(label="File", menu = file)

        Tables = Menu(top)
        Tables.add_command(label="Open tables", command=self.Select_table)
        Tables.add_command(label="Select Database", command=self.Select_base)
        top.add_cascade(label="Tables", menu=Tables)

    def Load_data(self):
        if self.Data_name:
            Sc = ScrolledList(self, ("Books", "Readers", "Orders"), self.Table_name, "selected table")
            self.Table_name = Sc.name
            Path = askopenfilename(initialdir = os.path.abspath(os.curdir)[:8] + "Data",
                                   filetypes=[("Text files",".txt"),("CSV files", ".csv")] )
            Path = ("'" + Path + "'")
            if Path != '':
                self.Lib.load_data(Path, self.Table_name)
        elif not self.Lib.connected:
            self.dialog = MyDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()
                self.Load_data()
        else:
            self.Select_base()
            self.Load_data()

    def Save(self):
        if self.rows!= []:
            if self.Lib.connected:
                self.fields = tuple(("id," + self.Lib.keys[self.Table_name][0][1:-1]).split(','))
                self.Strings = [self.fields] + self.Lib.get_strings(self.Table_name)

                for i in range(len(self.Types[self.Table_name])): #Проверяем и меняем названия столбцов
                    data = self.rows[0][i].get()
                    if data != self.Strings[0][i]:
                        self.Lib.rename_column(self.Table_name, self.Strings[0][i], data, self.Types[self.Table_name][i])

                for i in range(1,len(self.rows)):
                    for j in range(len(self.Types[self.Table_name])):
                        data = self.rows[i][j].get()
                        if self.Types[self.Table_name][j] == "int":
                            data = int(data)
                        if self.Types[self.Table_name][j] == "data":
                            data = datetime.date(data)
                        if data != self.Strings[self.Fiend_id(int(self.rows[i][0].get()))][j] and j != 0:
                            self.Lib.Change_data(self.Table_name, self.fields[j], self.rows[i][0].get(), data, self.Types[self.Table_name][j])
                showwarning("Saved", "Changes was saved!")
            else:
                showwarning("warning", "No one table was selected!")

    def Fiend_id(self, id):
        for i in range(len(self.Strings)):
            if self.Strings[i][0] == id:
                return i

    def Select_base(self):
        if self.Lib.connected:
            sc = ScrolledList(root, self.Lib.table_list(self.dialog.login, self.dialog.password, '127.0.0.1'), self.Data_name, "selected database")
            self.Data_name = sc.name
            if self.Data_name != '':
                try:
                    self.Lib.get_connection(self.dialog.login, self.dialog.password, '127.0.0.1', self.Data_name)
                except:
                    self.Data_name = ''
                    showerror("Fail", "The database does not exist")
        else:
            self.dialog = MyDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()

    def Select_table(self, flag = True):
        if self.Lib.connected:
            sc = ScrolledList(root,("Books", "Readers", "Orders"), self.Table_name, "selected table")
            self.Table_name = sc.name
            if flag:
                self.Show_table()
        else:
            self.dialog = MyDialog(root, self.Lib)
            if self.Lib.connected:
                self.Select_base()
                if  self.Data_name != '':
                    self.Select_table()

    def Show_table(self):
        if self.rows != []:
            self.Destroy_table()
        self.rows = []
        self.max_rows = self.Lib.Max(self.Table_name)
        if self.max_rows:
            self.max_cols = self.Lib.keys[self.Table_name][1].count('%s') +1
            self.fields = tuple(("id,"+self.Lib.keys[self.Table_name][0][1:-1]).split(','))
            self.Strings =[self.fields]+self.Lib.get_strings(self.Table_name)
            for i in range(self.max_rows):
                self.cols = []
                for j in range(self.max_cols):
                    ent = Entry(relief=RIDGE)
                    ent.grid(row=i+1, column=j, sticky=NSEW)
                    if j < self.max_cols:
                        ent.insert(END,self.Strings[i][j])
                    self.cols.append(ent)
                self.rows.append(self.cols)
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
            self.dialog = MyDialog(root, self.Lib)
            if self.Lib.connected:
                self.new_data()

    def Search(self):
        Search_dialog(root, self)

    def add_strs(self,data):
        self.rows = []
        for i in range(len(data)):
            self.cols = []
            for j in range(len(data[i])):
                ent = Entry(relief=RIDGE)
                ent.grid(row=i + 1, column=j, sticky=NSEW)
                ent.insert(END, data[i][j])
                self.cols.append(ent)
            self.rows.append(self.cols)

    def add_column(self, column_name, Data = None):
        ent = Entry(relief=RIDGE)
        ent.grid(row=1, column=len(self.rows[0]), sticky=NSEW)
        ent.insert(END, column_name)
        self.rows[0].append(ent)
        if len(Data) <= len(self.rows):
            if Data:
                for i in range(len(Data)):
                    ent = Entry(relief=RIDGE)
                    ent.grid(row=i+2, column=len(self.rows[0])-1, sticky=NSEW)
                    ent.insert(END, Data[i])
                    self.rows[i+1].append(ent)


    def Destroy_table(self):
        for i in range(len(self.rows)):
            for j in range(len(self.rows[i])):
                self.rows[i][j].destroy()

if __name__ == '__main__':
    root = Tk()
    app = Main(root)
    app.grid()

    Path = os.path.abspath(os.curdir)

    toolbar = Frame(root,relief = SUNKEN)
    toolbar.grid(row=0,column=0,sticky=NW)

    imgobj = Image.open(Path[:Path.find("Scripts")] + "Graphics\\"  + "diskette.jpg")
    img = PhotoImage(imgobj)
    btn_save = Button(toolbar, image=img, command= app.Save)
    btn_save.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_save, "Save table")

    imgobj2 = Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "rules.png")
    imgobj2.thumbnail((32,32), Image.ANTIALIAS)
    img2 = PhotoImage(imgobj2)
    btn_load = Button(toolbar, image=img2, command=app.Select_table)
    btn_load.config(width=32,height=32)
    btn_load.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_load, "Show table")

    imgobj3 = Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "new-database.png")
    imgobj3.thumbnail((32, 32), Image.ANTIALIAS)
    img3 = PhotoImage(imgobj3)
    btn_new = Button(toolbar, image=img3, command=app.new_data)
    btn_new.config(width=32, height=32)
    btn_new.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_new, "Create database")

    imgobj4 = Image.open(Path[:Path.find("Scripts")] + "Graphics\\" + "Search.png")
    imgobj4.thumbnail((32, 32), Image.ANTIALIAS)
    img4 = PhotoImage(imgobj4)
    btn_search = Button(toolbar, image=img4, command=app.Search)
    btn_search.config(width=32, height=32)
    btn_search.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_search, "Search")

    imgobj5 = Image.open(Path[:Path.find("Scripts")] + "Graphics\\" +"Del2.png")
    imgobj5.thumbnail((32, 32), Image.ANTIALIAS)
    img5 = PhotoImage(imgobj5)
    btn_Del = Button(toolbar, image=img5, command=None)
    btn_Del.config(width=32, height=32)
    btn_Del.pack(side=LEFT)
    btn_ttp = CreateToolTip(btn_Del, "Удалить строку")

    root.title('Library Base')
    root.mainloop()
