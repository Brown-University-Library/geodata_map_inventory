# Ethan McIntosh - GIS and Data Services - Brown University - summer 2022

# This is where the GUI will actually run (where the user window is configured, 
# and where calls to the backend are made in response to user selections)

import tkinter as tk
from tkinter import *
from tkinter import ttk
# from tkinter.messagebox import showinfo  # for messageboxes, if desired
import file_io
from collections import OrderedDict
from functools import partial

tool_title = 'Brown University Map Collection Inventory Tool'

# -------------- methods under construction -----------------
def record_exception():
    """
    Defines action that's taken when the Record exception button is pressed
    """
    pass

def remove_record():
    """
    Defines action that's taken when the Remove selected record button is pressed
    """
    pass

def we_have_1():
    """
    Defines action that's taken when the We have 1 button is pressed
    """
    pass

def we_have_multiple():
    """
    Defines action that's taken when the We have multiple button is pressed
    """
    pass

# ------------------- initialize tkinter window -----------------

root = tk.Tk()
root.title(tool_title)
# root.geometry('1220x250') # to manually set the size - shouldn't be necessary

# Frame containing the entire window - exists in order to customize margins
content = tk.Frame(root)
content.grid(row=0, column=0, padx=10, pady=20)

# ---------------------- header frame ----------------------------
header = tk.Frame(content)
header.grid(row=0, column=0, columnspan=5, rowspan=1, pady=5)
title = tk.Label(header, text=tool_title)
title.grid(row=0, column=0, columnspan=5, rowspan=1, pady=5)

# -------------------- options frame ----------------------
options = tk.Frame(content)
options.grid(row=1, column=0, columnspan=5, rowspan=5, pady=5)
dropdowns = OrderedDict()
class LabeledDropDownMenu:
    def __init__(self, label, menu, index):
        self.label = label
        self.menu = menu
        self.index = index
label_names = ['Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year']
for idx, lbl in enumerate(label_names):
    dropdowns[lbl] = LabeledDropDownMenu(ttk.Label(options, text=lbl + ": ")
        , ttk.Combobox(options, state=DISABLED)
        , idx)
# for example, dropdowns['Cell Name'].menu['state'] = 'readonly'

# gridding the drop downs onto the frame
for idx, dd in enumerate(dropdowns.values()):
    r = idx%3 + 1  # creates three rows of drop downs, starting at row 1, with
    c = int(idx/3)*2 # as many columns as are needed for the set of drop downs
    dd.label.grid(row=r, column=c, padx=20, pady=10)
    dd.menu.grid(row=r, column=c+1, padx=20)

# set up possible values for drop-downs
maps = {}
file_io.read_topos('usgs_topos.csv', maps)

def dd_selected(cur_dd): 
    """given a selection in a given drop-down menu, control configuration of other drop-downs"""
    if cur_dd.index == len(label_names) - 1:  # if the selected dropdown is the last one
        return None # exit this method without doing anything
    # otherwise, activate the next drop down menu
    next_dd = dropdowns[label_names[cur_dd.index + 1]]
    # we need something like a working_dict, or maybe a loop of the currently active dds getting their values?
    working_dict = maps
    for dd in list(dropdowns.values())[:next_dd.index]: # loop through the currently active drop downs
        val = dd.menu.get()
        if val.isnumeric():
            val = int(val)
        working_dict = working_dict[val]  # drill down into the appropriate dict based on selections
    vals = sorted(list(working_dict.keys()))
    next_dd.menu['values'] = vals # populate next drop-down with possible values
    for dd in list(dropdowns.values())[next_dd.index:]: # should maybe blank out & disable rest of drop-down menus
        dd.menu.set('')
        dd.menu['state'] = 'disabled'
    if len(vals) == 1:
        val = vals[0]
        if val == '':
            val = '(none)'
        next_dd.menu.set(val)
        next_dd.menu['state'] = 'disabled'
        dd_selected(next_dd)
    else:
        next_dd.menu['state'] = 'readonly'  # take next drop-down out of disabled state

# the for loop below does not work because lambdas refer to the variable dd rather
# than to its value at each 
#
# for dd in list(dropdowns.values()):
#     dd.menu.bind('<<ComboboxSelected>>', lambda event: dd_selected(dd))
scale_dd = dropdowns['Map Scale'].menu
scale_dd['values'] = sorted(list(maps.keys())) # or whatever corresponding dict's keys
scale_dd['state'] = 'readonly'
scale_dd.bind('<<ComboboxSelected>>', lambda event: dd_selected(dropdowns['Map Scale'])) 

state_dd = dropdowns['Primary State'].menu
state_dd.bind('<<ComboboxSelected>>', lambda event: dd_selected(dropdowns['Primary State']))
cell_name_dd = dropdowns['Cell Name'].menu
cell_name_dd.bind('<<ComboboxSelected>>', lambda event: dd_selected(dropdowns['Cell Name']))
map_year_dd = dropdowns['Map Year'].menu
map_year_dd.bind('<<ComboboxSelected>>', lambda event: dd_selected(dropdowns['Map Year']))
print_year_dd = dropdowns['Print Year'].menu
print_year_dd.bind('<<ComboboxSelected>>', lambda event: dd_selected(dropdowns['Print Year']))

# def stateSelected(event): 
#     """control cell name dropdown in response to state selection"""
#     dropdowns['Cell Name'].menu['values'] = sorted(list(maps[int(scale_dd.get())][state_dd.get()].keys()))
#     dropdowns['Cell Name'].menu.set('')
#     dropdowns['Cell Name'].menu['state'] = 'readonly'


# need to think through how button click methods are organized. i'd love to have the
# dropdowns in an ordered list, and then have methods that activate the "next"
# menus, or if making a selection of something earlier, deactivate previous ones
# Except at any given time, someone could be choosing any of the buttons. so i 
# do need named references to each one, i think.  Could still order them somehow
# though.  

dmgvar = BooleanVar(value=False)
damaged = ttk.Checkbutton(options, text="Something is significantly damaged", 
            variable=dmgvar, onvalue=True)
damaged.grid(row=3, column=2, columnspan=2)

exception_btn = ttk.Button(options, text='Record an exception', command=record_exception)
exception_btn.grid(row=4, column=0, pady=5)

remove_btn = ttk.Button(options, text='Remove selected record', command=remove_record)
remove_btn.grid(row=5, column=0, pady=5)

add1_btn = ttk.Button(options, text='We have 1', command=we_have_1)
add1_btn.grid(row=4, column=2, rowspan=2, pady=5)

add_mult_btn = ttk.Button(options, text='We have multiple', command=we_have_multiple)
add_mult_btn.grid(row=4, column=3, rowspan=2, pady=5)

# ---------------- table frame ---------------------------
table = tk.Frame(content)
table.grid(row=6, column=0, columnspan=5, rowspan=1, pady=5)
tbl_cols = ('Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year')
tbl = ttk.Treeview(table, columns=tbl_cols, show='headings')
tbl.grid(row=6, column=0, columnspan=4, rowspan=1)
# define headings
for col in tbl_cols:
    tbl.heading(col, text=col)
    tbl.column(col, width=100)
# add a scrollbar
tbl_scroll = ttk.Scrollbar(table, orient=tk.VERTICAL, command=tbl.yview)
tbl.configure(yscroll=tbl_scroll.set)
tbl_scroll.grid(row=6, column=4, rowspan=1, sticky='ns') # one column to the right of tbl

# --------------------- testing stuff out ----------------------

# ct_years = {
#     'USA': [1918, 1920, 1999]
#     , 'Canada': [1955, 1988, 2012]
#     , 'Australia': [1899, 1928, 1972]
# }

# othervar = StringVar()
# other = ttk.Combobox(content, textvariable=othervar, state=DISABLED)
# # other['values'] = []
# # other.state(["readonly"])
# other.grid(row=0, column=4)

# countryvar = StringVar()
# country = ttk.Combobox(content, textvariable=countryvar)
# country['values'] = ['USA', 'Canada', 'Australia']
# country.state(["readonly"])
# country.grid(row=0, column=3)
# def countrySelected(event): # control other dropdowns in response to selections
#     other['values'] = ct_years[country.get()]
#     other.set('') # or we may want to set it to the first elem of the list
#     other['state'] = 'readonly'
# country.bind('<<ComboboxSelected>>', countrySelected) 

# # define columns for table display
# columns = ('first_name', 'last_name', 'email')

# tree = ttk.Treeview(content, columns=columns, show='headings')

# # define headings
# for col in columns:
#     tree.heading(col, text=col)

# # generate sample data
# contacts = []
# for n in range(1, 100):
#     contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))

# # add data to the treeview
# for contact in contacts:
#     tree.insert('', tk.END, values=contact) # replace tk.END with 0 for addFirst


# def item_selected(event): # aka when rows of the table display are selected
#     for selected_item in tree.selection():
#         item = tree.item(selected_item)
#         record = item['values'] # list of the values in the row (could be appended)
#         # # show a message
#         # showinfo(title='Information', message=','.join(record))


# tree.bind('<<TreeviewSelect>>', item_selected)

# tree.grid(row=2, column=1, sticky='nsew', pady=10)

# # add a scrollbar
# scrollbar = ttk.Scrollbar(content, orient=tk.VERTICAL, command=tree.yview)
# tree.configure(yscroll=scrollbar.set)
# scrollbar.grid(row=2, column=2, sticky='ns') # one column to the right of tree

# run the app
root.mainloop()