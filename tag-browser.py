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
from tkinter import messagebox

import subprocess
import os

class TaggedItem():
    """Item in database. Stores tags related to file."""
    def __init__(self, filename: str, dispname: str="", tags: list[str]=[]):
        self.__filename = ""
        self.__dispname = dispname
        self.__tags = tags

        self.set_filename(filename)

    def add_tag(self, tag: str):
        self.__tags.append(tag)

    def remove_tag(self, tag: str):
        if tag in self.__tags:
            self.__tags.remove(tag)

    def is_tagged(self, tag: int) -> bool:
        if tag in self.__tags:
            return True
        return False

    def set_filename(self, fname: str):
        """Checks if path exists before setting"""
        if os.path.isfile(fname):
            self.__filename = fname
        else:
            raise FileNotFoundError

    def set_dispname(self, dname: str):
        self.__dispname = dispname

    def get_filename(self) -> str:
        return self.__filename

    def get_dispname(self) -> str:
        return self.__dispname

    def get_tags(self) -> list[str]:
        return self.__tags


class AddDialog(simpledialog.Dialog):
    """Dialog for adding an item into the database."""
    def __init__(self, *args, **kwargs): 
        self.filename = ""
        self.dispname = StringVar()
        self.tags = StringVar()
        super().__init__(*args, **kwargs)

    def __cbk_filedlg(self):
        """Callback for opening file dialog"""
        self.filename = filedialog.askopenfilename()
        self.fbtn["text"] = self.filename

    def body(self, master):
        # mainframe for dlg
        mf = ttk.Frame(master)
        mf.grid(row=0,column=0,sticky=(N,E,W,S))
        
        # Choose file button opens file dlg
        ttk.Label(mf, text="Choose File:").grid(row=1,column=0,sticky=(E))
        self.fbtn = ttk.Button(mf, text="...",command=self.__cbk_filedlg)
        self.fbtn.grid(row=1,column=1,sticky=(N,E,W,S))

        # Entry for writing display name
        ttk.Label(mf, text="Display Name:").grid(row=2,column=0,sticky=(E))
        ttk.Entry(mf,textvariable=self.dispname).grid(row=2,column=1,
                                                      sticky=(N,E,W,S))
        
        # Entry for writing tags (csv)
        ttk.Label(mf, text="Tags (CSV):").grid(row=3,column=0,sticky=(E))
        ttk.Entry(mf,textvariable=self.tags).grid(row=3,column=1,
                                                  sticky=(N,E,W,S))

        return master


class Window(Tk):
    """Main Tkinter window. Handles program logic & displaying."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save before closing please
        self.protocol("WM_DELETE_WINDOW", self.save)

        # Store items in "database"
        self.__items = []

        # Mainframe for displaying stuff
        self.frame = ttk.Frame(self)
        self.frame.grid(column=0, row=0, sticky=(N,E,W,S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Top button bar
        buttonbar = ttk.Frame(self.frame, relief="raised", borderwidth=3)
        buttonbar.grid(row=0,column=0,sticky=(N,E,W,S))

        addbtn = ttk.Button(buttonbar, text="Add", command=self.__cbk_add)
        addbtn.grid(row=0,column=0,sticky=(N,E,S))

        # Searchbar
        self.searchval = StringVar()
        self.searchbar = ttk.Entry(self.frame, textvariable=self.searchval)
        self.searchbar.grid(column=0, row=1, sticky=(N,E,W,S))
        self.frame.columnconfigure(0, weight=1)

        # Search results frame
        self.resultsframe = ttk.Frame(self.frame, relief="sunken", borderwidth=3)
        self.resultsframe.grid(row=2, column=0, sticky=(N,E,W,S))
        self.frame.rowconfigure(2, weight=1)

        # Search results treeview
        self.tree = ttk.Treeview(self.resultsframe, columns=("fname","tags"))
        self.tree.heading("fname", text="Filename")
        self.tree.heading("tags", text="Tagged")
        self.tree.bind("<Double-1>", self.__click_tree)
        self.tree.grid(row=0,column=0, sticky=(N,E,W,S))
        self.resultsframe.columnconfigure(0, weight=1)
        self.resultsframe.rowconfigure(0, weight=1)


        self.load()

    def save(self):
        """Save items to file. Each line is an item in the dict, value
        separated by pipe character."""
        fptr = open("dict.csv", "w")
        for i in self.__items:
            tag_str = ", ".join(i.get_tags())
            fptr.write(i.get_filename() + "|" + i.get_dispname() + "|"
                       + " ".join(tag_str.split())+ "\n")

        fptr.close()
        self.destroy()

    def load(self):
        """Load items from file. Clears dict upon loading."""
        self.__items = []

        fptr = open("dict.csv", "r")
        for i in fptr:
            values = i.strip("\n").split("|")
            print(values)
            try:
                ti = TaggedItem(values[0], dispname=values[1],
                                           tags=values[2].split(","))
                self.__items.append(ti)
            except FileNotFoundError:
                messagebox.showerror(message=values[1] + " is not a valid file!\
                                     Item has been removed from dictionary.")
            

        self.tree_redraw()


    def __click_tree(self, event):
        """Callback for clicking an item on the treeview. Opens zathura."""
        item = self.tree.selection()[0]
        print(self.tree.item(item, "values")[0])
        subprocess.call(["zathura",self.tree.item(item, "values")[0]])

    def __cbk_add(self):
        """Callback for pressing "Add..." button."""
        correct_format = False
        while not(correct_format):
            try:
                dlg = AddDialog(self)

                # Format tags from dialog into proper format
                tags = "".join(dlg.tags.get().strip()).split(",")
                print(tags)
                ti = TaggedItem(dlg.filename, dispname=dlg.dispname.get(),
                                tags=tags)
                correct_format = True
            except FileNotFoundError:
                messagebox.showerror(message="File specified is not valid. \
                                                Please choose another.")

        # Add only if correct format
        self.__items.append(ti)
        self.tree_redraw()

    def tree_redraw(self):
        """Redraw treeview from scratch. Call when
        adding/removing/editing TaggedItem."""
        self.tree.delete(*self.tree.get_children())

        for item in self.__items:
            tag_str = ", ".join(item.get_tags())
            self.tree.insert("", END, text=item.get_dispname(),
                             values=(item.get_filename(),
                                     " ".join(tag_str.split())))


win = Window()
win.mainloop()
