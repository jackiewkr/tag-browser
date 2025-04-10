"""tag-browser

PDF file organizer meant for tagging files to be later searched for via
tags.

Jacqueline W.

Licensed under MPLv2
"""

from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import filedialog

import subprocess

class TaggedItem():

    def __init__(self, filename, dispname="", tags=""):
        self.filename = filename
        self.dispname = dispname
        self.tags = tags

    def add_tag(self, tag):
        self.tags.append(tag)

    def is_tagged(self, tag):
        if tag in self.tags:
            return True
        return False

class AddDialog(simpledialog.Dialog):
    def __init__(self, *args, **kwargs): 
        self.filename = ""
        self.dispname = StringVar()
        self.tags = StringVar()
        super().__init__(*args, **kwargs)

    def __cbk_filedlg(self):
        self.filename = filedialog.askopenfilename()
        self.fbtn["text"] = self.filename

    def body(self, master):
        mf = ttk.Frame(master)
        mf.grid(row=0,column=0,sticky=(N,E,W,S))
        
        ttk.Label(mf, text="Choose File:").grid(row=1,column=0,sticky=(E))
        self.fbtn = ttk.Button(mf, text="...",command=self.__cbk_filedlg)
        self.fbtn.grid(row=1,column=1,sticky=(N,E,W,S))

        ttk.Label(mf, text="Display Name:").grid(row=2,column=0,sticky=(E))
        ttk.Entry(mf,textvariable=self.dispname).grid(row=2,column=1,sticky=(N,E,W,S))

        ttk.Label(mf, text="Tags (CSV):").grid(row=3,column=0,sticky=(E))
        ttk.Entry(mf,textvariable=self.tags).grid(row=3,column=1,sticky=(N,E,W,S))


        return master


class Window(Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.protocol("WM_DELETE_WINDOW", self.save)

        self.__items = []

        self.frame = ttk.Frame(self)
        self.frame.grid(column=0, row=0, sticky=(N,E,W,S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # button bar
        buttonbar = ttk.Frame(self.frame, relief="raised", borderwidth=3)
        buttonbar.grid(row=0,column=0,sticky=(N,E,W,S))

        addbtn = ttk.Button(buttonbar, text="Add", command=self.__cbk_add)
        addbtn.grid(row=0,column=0,sticky=(N,E,S))

        # searchbar
        self.searchval = StringVar()
        self.searchbar = ttk.Entry(self.frame, textvariable=self.searchval)
        self.searchbar.grid(column=0, row=1, sticky=(N,E,W,S))
        self.frame.columnconfigure(0, weight=1)

        # search results frame
        self.resultsframe = ttk.Frame(self.frame, relief="sunken", borderwidth=3)
        self.resultsframe.grid(row=2, column=0, sticky=(N,E,W,S))
        self.frame.rowconfigure(2, weight=1)

        # search results treeview
        self.tree = ttk.Treeview(self.resultsframe, columns=("fname","tags"))
        self.tree.heading("fname", text="Filename")
        self.tree.heading("tags", text="Tagged")
        self.tree.bind("<Double-1>", self.__click_tree)
        self.tree.grid(row=0,column=0, sticky=(N,E,W,S))
        self.resultsframe.columnconfigure(0, weight=1)
        self.resultsframe.rowconfigure(0, weight=1)

        self.load()

    def save(self):
        fptr = open("dict.csv", "w")
        for i in self.__items:
            fptr.write(i.filename + "|" + i.dispname + "|" + i.tags)

        fptr.close()
        self.destroy()

    def load(self):
        self.__items = []

        fptr = open("dict.csv", "r")
        for i in fptr:
            values = i.split("|")
            self.__items.append(TaggedItem(values[0], dispname=values[1], tags=values[2]))
        self.tree_redraw()


    def __click_tree(self, event):
        item = self.tree.selection()[0]
        print(self.tree.item(item, "values")[0])
        subprocess.call(["zathura",self.tree.item(item, "values")[0]])

    def __cbk_add(self):
        dlg = AddDialog(self)

        self.__items.append(TaggedItem(dlg.filename, dispname=dlg.dispname.get(), tags=dlg.tags.get()))
        self.tree_redraw()

    def tree_redraw(self):
        self.tree.delete(*self.tree.get_children())

        for item in self.__items:
            self.tree.insert("", END, text=item.dispname, values=(item.filename, item.tags))




win = Window()
win.mainloop()
