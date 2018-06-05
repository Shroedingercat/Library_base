from tkinter import *
from PIL.ImageTk import PhotoImage
import os


class ScrolledList(Toplevel):
    def __init__(self,root, options, name, Text):
        super().__init__(root)
        self.name = name  # запретить доступ к др. окнам, пока открыт диалог
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("+{}+{}".format(int(w / 2.2), int(h / 2.3)))
        imgicon = PhotoImage(file=os.path.abspath(os.curdir)[:8] + "Graphics\\" + "logo3.png")
        self.tk.call('wm', 'iconphoto', self._w, imgicon)
        Label(self,text=Text).pack()
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

