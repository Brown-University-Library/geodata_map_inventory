# Ethan McIntosh - GIS and Data Services - Brown University - August 2022

# the LabeledDropDownMenu class groups together several tk widgets (a label, 
# menu, and prev/next buttons) along with data that helps link each LDDM to the
# next one in a hierachy (next_vals).

import tkinter as tk
from tkinter import ttk

class LabeledDropDownMenu:
    """label is a tk label, menu is the corresponding tk combobox, 
    index is the position of this drop-down menu in the hierarchy of menus (evaluate whether this is necessary),
    from_dict is the dictionary whose keys are the possible items in the menu.
    may also have prev and next tk buttons as part of this object"""
    def __init__(self, label, menu, prev, next, index, next_vals):
        self.label = label
        self.menu = menu
        self.index = index
        self.prev = prev
        self.next = next
        self.next_vals = next_vals

    def disable(self):
        self.menu['state'] = tk.DISABLED
        self.prev['state'] = tk.DISABLED
        self.next['state'] = tk.DISABLED

    def enable(self):
        self.menu['state'] = tk.NORMAL
        self.prev['state'] = tk.NORMAL
        self.next['state'] = tk.NORMAL