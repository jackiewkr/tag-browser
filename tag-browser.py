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
    def __init__(self, uid: int, filename: str, dispname: str="",
                 tags: list[str]=[]):
        self.uid = uid
        self.__filename = ""
        self.__dispname = dispname
        self.__tags = tags

        self.set_filename(filename)

    def set_tags(self, tags: list[str]):
        self.__tags = []
        for tag in tags:
            self.__tags.append(tag.strip())

    def is_tagged(self, tag: str) -> bool:
        print(tag + ": ->" + ",".join(self.__tags))
        for i in self.__tags:
            print("'"+i.strip()+"'")
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
        self.__dispname = dname

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

class ModDialog(simpledialog.Dialog):
    """Dialog for modifying an item into the database.
    TODO: merge into one dialog?"""
    def __init__(self, parent, ti): 
        self.filename = ti.get_filename()
        self.dispname = StringVar()
        self.tags = StringVar()

        self.dispname.set(ti.get_dispname())
        self.tags.set(", ".join(ti.get_tags()))
        super().__init__(parent)

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
        self.fbtn = ttk.Button(mf, text=self.filename, 
                               command=self.__cbk_filedlg)
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
        self.__curr_items = []
        self.__cntr = 0;

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
        self.searchbar.bind("<Return>", self.__cbk_search)
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

        # Context menu for popup on treeview
        self.contextmenu = Menu(self.tree)
        self.tree.bind("<Button-3>", self.__cbk_context)


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
        self.__cntr = 0;
        for i in fptr:
            values = i.strip("\n").split("|")
            tags = []
            for i in values[2].split(","):
                tags.append(i.strip())
            try:
                ti = TaggedItem(self.__cntr, values[0], dispname=values[1], tags=tags)
                self.__items.append(ti)
                self.__cntr += 1;
            except FileNotFoundError:
                messagebox.showerror(message=values[1] + " is not a valid file!\
                                     Item has been removed from dictionary.")
            
        self.__curr_items = self.__items
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
                ti = TaggedItem(self.__cntr, dlg.filename,
                                dispname=dlg.dispname.get(), tags=tags)
                correct_format = True
                self.__cntr += 1
            except FileNotFoundError:
                messagebox.showerror(message="File specified is not valid. \
                                                Please choose another.")

        # Add only if correct format
        self.__items.append(ti)
        self.tree_redraw()

    def __cbk_search(self, event):
        """Callback for searching a tag
        Tags are evaluated left to right

        TAG: search for tag
        !TAG: search for anything without tag
        TAG ATAG BTAG: seacrh for anything with all three tags"""
        criteria = self.searchval.get().split(" ")
        self.__curr_items = self.__items
        # early exit for empty searchbar
        if criteria[0] == "":
            self.tree_redraw()
            return

        for tok in criteria:
            temp_curr_items = []

            if tok[0] == "!":
                for item in self.__curr_items:
                    if item.is_tagged(tok[1:]) == False:
                        temp_curr_items.append(item)
            else:
                for item in self.__curr_items:
                    if item.is_tagged(tok):
                        temp_curr_items.append(item)

            self.__curr_items = temp_curr_items

        self.tree_redraw()

    def __cbk_modify(self, uid):
        """Callback for pressing "Modify item" menu button."""
        correct_format = False
        while not(correct_format):
            try:
                dlg = ModDialog(self, self.__items[uid])
                correct_format = True
            except FileNotFoundError:
                messagebox.showerror(message="File specified is not valid. \
                                                Please choose another.")
        tags = "".join(dlg.tags.get().strip()).split(",")

        # Add only if correct format
        self.__items[uid].set_filename(dlg.filename)
        self.__items[uid].set_dispname(dlg.dispname.get())
        self.__items[uid].set_tags(tags)

        self.tree_redraw()


    def __cbk_context(self, event):
        """Repopulate context menu with correct items relating to selected
        item. Handle other context menu tasks."""
        self.contextmenu.delete(0, "end")
        uid = int(self.tree.identify_row(event.y))
        self.tree.selection_set(uid)

        self.contextmenu.add_command(label="Modify item",
                                     command=lambda u=uid: self.__cbk_modify(u))
        self.contextmenu.add_command(label="Delete item",
                                     command=lambda u=uid: self.__cbk_delete(u))

        self.contextmenu.tk_popup(event.x_root, event.y_root)


    def tree_redraw(self):
        """Redraw treeview from scratch. Call when
        adding/removing/editing TaggedItem."""
        self.tree.delete(*self.tree.get_children())

        for item in self.__curr_items:
            tag_str = ", ".join(item.get_tags())
            self.tree.insert("", END, text=item.get_dispname(),
                             values=(item.get_filename(),
                                     " ".join(tag_str.split())), iid=item.uid)


win = Window()
win.mainloop()
