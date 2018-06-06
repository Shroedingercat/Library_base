from tkinter import *
from tkinter.messagebox import *
from PIL.ImageTk import PhotoImage
import os

class MyDialog(Toplevel):
    def __init__(self,root,Lib):
        super().__init__(root)
        self.Lib = Lib
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w/2.2),int(h/2.3)))
        self.resizable(False, False)
        Path = os.path.abspath(os.curdir)
        imgicon = PhotoImage(file=Path[:Path.find("Scripts")] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)
        Label(self, text="Enter login and password").grid(row=0, column=2)
        Label(self, text="login:").grid(row =1, column=1)
        Label(self, text="password:").grid(row=2, column=1)
        self.ent_login = Entry(self)
        self.ent_login.grid(row=1, column=2)
        self.ent_password= Entry(self, show="*")
        self.ent_password.grid(row=2, column=2)
        btn = Button(self, text="Ok", command=self.Check)
        btn.grid(row=3, column=2)
        self.focus_set()  # принять фокус ввода,
        self.grab_set()  # запретить доступ к др. окнам, пока открыт диалог
        self.wait_window()


    def Check(self):
        self.login = self.ent_login.get()
        self.password = self.ent_password.get()
        try:
            self.Lib.get_connection(self.login, self.password, '127.0.0.1')
            self.Lib.close_all()
            self.destroy()
        except:
            showwarning("Ok", "Wrong login or password")

