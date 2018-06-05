from tkinter import *

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
        self.lower_bound = float(self.ent.get())
        self.Upper_border = float(self.ent2.get())

        self.destroy()