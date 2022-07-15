# Ethan McIntosh - GIS and Data Services - Brown University - summer 2022

# This is where the GUI will actually run (where the user window is configured, 
# and where calls to the backend are made in response to user selections)

import tkinter as tk
from tkinter import *
from tkinter import ttk
# from tkinter.messagebox import showinfo  # for messageboxes, if desired
import file_io, db # other files in this package
from collections import OrderedDict

tool_title = 'Brown University Map Collection Inventory Tool'
map_db = db.Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/maps_we_have_test.db')

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
        self.menu['state'] = DISABLED
        self.prev['state'] = tk.DISABLED
        self.next['state'] = tk.DISABLED

    def enable(self):
        self.menu['state'] = 'readonly'
        self.prev['state'] = tk.NORMAL
        self.next['state'] = tk.NORMAL


# from_dict of the first menu is always the outer dict. every other from_dict is
# based on the selection of the dict above it

# -------------- methods under construction -----------------
def is_number(s):
    """This is part of my workaround for the fact that pandas casts integers in 
    columns with missing values as floats."""
    try:
        float(s)
        return True
    except ValueError:
        return False

def grab_dd_values():
    """traverses the drop-downs in order, returns a list of the selected values"""
    data = []
    for dd in dropdowns.values():
        data.append(dd.menu.get()) 
    return data

def multisort(elem):
    """sort by number if elem is numeric, sort alphabetically otherwise, and handle
    missing values filled in as '(none)' """
    if elem == '(none)':  # the value that was filled in for missing values in print year column
         return 0
    elif is_number(elem):
        return float(elem)
    else: 
        return elem

def dd_selected(cur_dd: LabeledDropDownMenu): 
    """given a selection in a given drop-down menu, control configuration of other drop-downs"""
    # disable the we have 1 and we have multiple buttons by default
    add1_btn['state'] = tk.DISABLED
    add_mult_btn['state'] = tk.DISABLED

    # if the user has made a selection for the last drop-down in the hierarchy,
    # activate the we have 1 and we have multiple buttons and exit this method
    if cur_dd.index == len(label_names) - 1:
        add1_btn['state'] = tk.NORMAL
        add_mult_btn['state'] = tk.NORMAL
        return None # exit this method without doing anything

    # otherwise (if the selection is for some other drop-down), we want to alter
    # the possible values of the next drop down menu in the hierarchy
    next_dd = dropdowns[label_names[cur_dd.index + 1]]
    next_dd.next_vals = cur_dd.next_vals[cur_dd.menu.get()]
    vals = sorted(list(next_dd.next_vals.keys()), key=multisort)
    next_dd.menu['values'] = vals
    

    # blank out & disable all drop-down menus after whichever one was selected
    # so that selections high in the hierarchy will clear out the following menus' values
    for dd in list(dropdowns.values())[next_dd.index:]: 
        dd.menu.set('')
        dd.disable()

    if len(vals) == 1:  # if there's only 1 possible value for the next drop down
        # lock that value into that drop-down menu and disable it from selections
        next_dd.menu.set(vals[0])
        next_dd.disable()
        # then, do what needs to be done in response to the next dd being selected
        dd_selected(next_dd)
    else: # if there are more than 1 possible values for the next drop down
        # activate the next drop down so the user can make a selection on it
        next_dd.enable()  

def prev_button(dd: LabeledDropDownMenu):
    """toggle the value on a given drop-down menu to its previous value"""
    # testing "prev" button for scale drop down
    val = dd.menu.current()
    if val != 0: # if we're not at the beginning of the list of possible values
        dd.menu.current(val - 1) # set the drop down to the next value in the list of possible values
        dd_selected(dd)

def next_button(dd: LabeledDropDownMenu):
    """toggle the value on a given drop-down menu to its previous value"""
    val = dd.menu.current()
    if val != len(dd.menu['values']) - 1: # if we're not at the end of the list of possible values
        dd.menu.current(val + 1) # set the drop down to the next value in the list of possible values
        dd_selected(dd)

def record_exception():
    """
    Defines action that's taken when the Record exception button is pressed
    """
    pass

def remove_record(scan_id):
    """deletes a given scan id from sqlite backend"""
    map_db.remove(scan_id)
    remaining = map_db.fetch(scan_id)
    if len(remaining) == 0:
        # call the method to display confirmation of removal
        print("removal success") # replace with message on gui display
    else:
        print("Possible error removing record from the database: ")
        print(remaining)
    pass

def remove_selected_record():
    """
    Defines action that's taken when the Remove selected record button is pressed
    """
    #get the scan id of whatever table record is selected
    # remove_record(scan_id)
    selected = tbl.focus()
    removal_id = tbl.item(selected, 'values')[0]
    # should print a confirmation message before executing the removal
    remove_record(removal_id)
    tbl.delete(tbl.selection())

def we_have_1():
    """
    Defines action that's taken when the We have 1 button is pressed
    """
    # This method does not check whether all possible selections have been made,
    # because it is assumed that this method will only be called when all required 
    # criteria have been selected. 
    # This method does check if there are multiple records, and
    # if so, do whatever we do for multiples (present links, etc).
    # if it's just one record, insert it into the table.

    last_dd = list(dropdowns.values())[len(dropdowns)-1]
    results = last_dd.next_vals[last_dd.menu.get()] # should be a list of tuples
    if len(results) == 1:
        insert_record(results[0][0])  # passing in just the scan ID
    else:
        print("multiple matches")  # do whatever we are doing to do for multiple matching records

def we_have_multiple():
    """
    Defines action that's taken when the We have multiple button is pressed
    """
    pass

def insert_record(scan_id):
    """inserts record for map we have on hand into sqlite backend, confirms the
    insertion by selecting that record from the db, and then calls methods to add
    that record to the table frame and print out a message, etc"""
    # maybe insert, then fetch for confirmation?
    before = map_db.fetch(scan_id)
    if len(before) > 0:
        print("that map has already been recorded")
        return None
    map_db.insert(scan_id)
    inserted = map_db.fetch(scan_id)
    if len(inserted) == 1:
        add_to_table(scan_id) # display record on table, as well as confirmation
        print("insert success")
        pass
    else:
        print("Possible error inserting record into the database: ")
        print(inserted)
    pass

def add_to_table(scan_id):
    """insert info about a map we have into the display table"""
    tbl_vals = [scan_id, 'USGS']
    tbl_vals.extend(grab_dd_values())
    # replace 'no' with dupe_var once created 
    tbl_vals.extend([dmgvar.get(), 'no'])
    tbl.insert('', 0, values=tbl_vals)
    # will need scan id, damaged y/n, and quantity as columns as well
    # ('Scan ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year', 'Damaged', 'Duplicate')

def sign_in(event):
    """selection is made on the initials drop down"""
    if initials.get() not in initials['values']: # if someone types in a new username
        # add their entry to the drop-down of possible values
        initials['values'] = (*initials['values'], initials.get())
        # and save the possible values to users.csv
        file_io.write_users('users.csv', initials['values'])
    list(dropdowns.values())[0].enable()
    # maybe print a confirmation message that you're signed in?

# ------------------- initialize tkinter window -----------------

root = tk.Tk()
root.title(tool_title)
# root.geometry('1220x250') # to manually set the size - shouldn't be necessary

# Frame containing the entire window - exists in order to customize margins
content = tk.Frame(root)
content.grid(row=0, column=0, padx=10, pady=20)

# in the future, column and row spans should not be manually defined

# -------------------- options frame ----------------------
options = tk.Frame(content)
options.grid(row=1, column=0, columnspan=7, rowspan=8, pady=5)
dropdowns = OrderedDict()

label_names = ['Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year']
for idx, lbl in enumerate(label_names):
    dropdowns[lbl] = LabeledDropDownMenu(ttk.Label(options, text=lbl + ": ")
        , ttk.Combobox(options, state=DISABLED)
        , ttk.Button(options, text="^", state=DISABLED)
        , ttk.Button(options, text="v", state=DISABLED)
        , idx
        , {}
    )
# for example, dropdowns['Cell Name'].menu['state'] = 'readonly'

# gridding the drop downs onto the frame
for idx, dd in enumerate(dropdowns.values()):
    r = (idx%3)*2 + 1  # creates three rows of drop downs, starting at row 1, with
    c = int(idx/3)*3 # as many columns as are needed for the set of drop downs
    dd.label.grid(row=r, column=c, rowspan=2, padx=20, pady=10)
    dd.menu.grid(row=r, column=c+1, rowspan=2, padx=20)
    dd.prev.grid(row=r, column=c+2)
    dd.next.grid(row=r+1, column=c+2)
    # want to place prev and next buttons (^ and v ?) too

# set up possible values for drop-downs
maps = {}
file_io.read_topos('usgs_topos.csv', maps)

# initialize the first dropdown
first_dd = list(dropdowns.values())[0] # access the first labeled dropdown menu
first_dd.next_vals = maps
first_dd.menu['values'] = sorted(list(maps.keys()), key=multisort) # or whatever corresponding dict's keys
# first_dd['state'] = 'readonly'

# bind each dropdown to dd_selected with itself as an argument, and each prev or
# next button to the prev and next button methods with each dd as an argument
# the dd=dd statements are necessary - without it, the lambda would point to the 
# variable dd at the end of the for loop rather than its value at each iteration.
for dd in list(dropdowns.values()):
    dd.menu.bind('<<ComboboxSelected>>', lambda event, dd=dd: dd_selected(dd))
    dd.prev.configure(command = lambda dd=dd: prev_button(dd))
    dd.next.configure(command = lambda dd=dd: next_button(dd))  

dmgvar = BooleanVar(value=False)
damaged = ttk.Checkbutton(options, text="Something is significantly damaged", 
            variable=dmgvar, onvalue=True)
damaged.grid(row=5, column=3, columnspan=3, rowspan=2)

exception_btn = ttk.Button(options, text='Record an exception', command=record_exception)
exception_btn.grid(row=7, column=0, columnspan=3, pady=5)

remove_btn = ttk.Button(options, text='Remove selected record', command=remove_selected_record)
remove_btn.grid(row=8, column=0, columnspan=3, pady=5)

add1_btn = ttk.Button(options, text='We have 1', command=we_have_1, state=DISABLED)
add1_btn.grid(row=7, column=3, rowspan=2, pady=5)

add_mult_btn = ttk.Button(options, text='We have multiple', command=we_have_multiple, state=DISABLED)
add_mult_btn.grid(row=7, column=4, rowspan=2, pady=5)

# ---------------------- header frame ----------------------------
header = tk.Frame(content)
header.grid(row=0, column=0, columnspan=7, rowspan=1, pady=5)
title = ttk.Label(header, text=tool_title)
title.grid(row=0, column=0, columnspan=5, rowspan=1, padx=100, pady=5)

sign_in_label = ttk.Label(header, text="Select or type your initials:")
sign_in_label.grid(row=0, column=5)

users = []
file_io.read_users('users.csv', users)
initials = ttk.Combobox(header)
initials['values'] = users
initials.bind('<<ComboboxSelected>>', sign_in)
initials.bind('<Return>', sign_in)
initials.grid(row=0, column=6, padx=20)

# ---------------- table frame ---------------------------
table = tk.Frame(content)
table.grid(row=9, column=0, columnspan=7, rowspan=1, pady=5)
tbl_cols = ('Scan ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year', 'Damaged', 'Duplicate')
tbl = ttk.Treeview(table, columns=tbl_cols, show='headings')
tbl.grid(row=9, column=0, columnspan=6, rowspan=1)
# define headings
for col in tbl_cols:
    tbl.heading(col, text=col)
    tbl.column(col, width=100)
# add a scrollbar
tbl_scroll = ttk.Scrollbar(table, orient=tk.VERTICAL, command=tbl.yview)
tbl.configure(yscroll=tbl_scroll.set)
tbl_scroll.grid(row=9, column=6, rowspan=1, sticky='ns') # one column to the right of tbl

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


# --------- code for rendering images from URL into tkinter window, if desired ----------------

# import urllib.request
# import io
# from PIL import Image, ImageTk
# root = Tk()
# images = []
# fake_csv = [[1, "blue", 4, "pillow"], [2, "red", 12, "horse"]]
# mapthumb = 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/HistoricalTopo/PDF/AK/25000/AK_Anchorage%20B-7%20NW_353597_1979_25000_tn.jpg'

# for i in range(0, 1): # changed from 8 to 1 from https://stackoverflow.com/questions/38173526/displaying-images-from-url-in-tkinter
#     raw_data = urllib.request.urlopen(mapthumb).read()
#     im = Image.open(io.BytesIO(raw_data))
#     image = ImageTk.PhotoImage(im)
#     label1 = Label(root, image=image)
#     label1.grid(row=i, sticky=W)

#     # append to list in order to keep the reference
#     images.append(image)