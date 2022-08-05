# Ethan McIntosh - GIS and Data Services - Brown University - August 2022

# the LabeledDropDownMenu class groups together several tkinter widgets (a label, 
# menu, and prev/next buttons) along with data that helps link each LDDM to the
# next one in a hierachy (next_vals).

import tkinter as tk

class LabeledDropDownMenu:
    """label is a tkinter label, menu is the corresponding tkinter combobox, 
    index is the position of this drop-down menu in the hierarchy of menus (evaluate whether this is necessary),
    from_dict is the dictionary whose keys are the possible items in the menu.
    may also have prev and next tkinter buttons as part of this object"""
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
        self.menu['state'] = 'readonly'
        self.prev['state'] = tk.NORMAL
        self.next['state'] = tk.NORMAL