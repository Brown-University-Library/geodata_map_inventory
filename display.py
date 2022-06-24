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
# root.geometry('1220x250') # to manually set the size

label = ttk.Label(root, text='Full name:')
label.grid(row=0, column=0)

ct_years = {
    'USA': [1918, 1920, 1999]
    , 'Canada': [1955, 1988, 2012]
    , 'Australia': [1899, 1928, 1972]
}

othervar = StringVar()
other = ttk.Combobox(root, textvariable=othervar)
other['values'] = []
other.state(["readonly"])
other.grid(row=0, column=4)

countryvar = StringVar()
country = ttk.Combobox(root, textvariable=countryvar)
country['values'] = ['USA', 'Canada', 'Australia']
country.state(["readonly"])
country.grid(row=0, column=3)
def countrySelected(event): # control other dropdowns in response to selections
    other['values'] = ct_years[country.get()]
    other.set('') # or we may want to set it to the first elem of the list
country.bind('<<ComboboxSelected>>', countrySelected) 

# define columns for table display
columns = ('first_name', 'last_name', 'email')

tree = ttk.Treeview(root, columns=columns, show='headings')

# define headings
for col in columns:
    tree.heading(col, text=col)

# generate sample data
contacts = []
for n in range(1, 100):
    contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))

# add data to the treeview
for contact in contacts:
    tree.insert('', tk.END, values=contact) # replace tk.END with 0 for addFirst


def item_selected(event): # aka when rows of the table display are selected
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        record = item['values'] # list of the values in the row (could be appended)
        # # show a message
        # showinfo(title='Information', message=','.join(record))


tree.bind('<<TreeviewSelect>>', item_selected)

tree.grid(row=2, column=1, sticky='nsew', pady=10)

# add a scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=2, column=2, sticky='ns') # one column to the right of tree

# run the app
root.mainloop()