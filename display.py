# Ethan McIntosh - GIS and Data Services - Brown University - summer 2022

# This is where the GUI will actually run.  This is where the user view is 
# configured, and where user selections are handled through calls to the backend

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo  # for messageboxes, if desired

tool_title = 'Brown University Map Collection Inventory Tool'

root = tk.Tk()
root.title(tool_title)
# root.geometry('820x250') # to manually set the size

content = tk.Frame(root)
content.grid(row=0, column=0, padx=10, pady=20)

header = tk.Frame(content)
header.grid(row=0, column=0, columnspan=5, rowspan=1, pady=5)
title = tk.Label(header, text=tool_title)
title.grid(row=0, column=0, columnspan=5, rowspan=1, pady=5)

options = tk.Frame(content)
options.grid(row=1, column=0, columnspan=5, rowspan=5, pady=5)
dropdowns = {}
class LabeledDropDownMenu:
    def __init__(self, label, menu):
        self.label = label
        self.menu = menu
label_names = ['Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year']
for lbl in label_names:
    dropdowns[lbl] = LabeledDropDownMenu(ttk.Label(options, text=lbl + ": ")
        , ttk.Combobox(options, textvariable=StringVar(), state=DISABLED))
# for example, dropdowns['Cell Name'].menu['state'] = 'readonly'

for idx, dd in enumerate(dropdowns.values()):
    r = idx%3 + 1  # creates three rows of drop downs, starting at row 1, with
    c = int(idx/3)*2 # as many columns as are needed for the set of drop downs
    side = tk.W if idx < 3 else tk.E
    dd.label.grid(row=r, column=c, padx=20, pady=10)
    dd.menu.grid(row=r, column=c+1, padx=20)

dmgvar = BooleanVar(value=False)
damaged = ttk.Checkbutton(options, text="Something is significantly damaged", 
            variable=dmgvar, onvalue=True)
damaged.grid(row=3, column=2, columnspan=2)

def record_exception():
    pass

def remove_record():
    pass

def we_have_1():
    pass

def we_have_multiple():
    pass

exception_btn = ttk.Button(options, text='Record an exception', command=record_exception)
exception_btn.grid(row=4, column=0, columnspan=2, pady=5)

remove_btn = ttk.Button(options, text='Remove selected record', command=remove_record)
remove_btn.grid(row=5, column=0, columnspan=2, pady=5)

add1_btn = ttk.Button(options, text='We have 1', command=we_have_1)
add1_btn.grid(row=4, column=2, rowspan=2, pady=5)

add_mult_btn = ttk.Button(options, text='We have multiple', command=we_have_multiple)
add_mult_btn.grid(row=4, column=3, rowspan=2, pady=5)

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