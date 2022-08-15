# Ethan McIntosh - GIS and Data Services - Brown University - August 2022

# This is where the GUI will actually run (where the user window is configured, 
# and where calls to the backend are made in response to user selections)

from lddm import *
from tkinter import *
from tkinter import ttk
import file_io, db # other files in this package
from collections import OrderedDict
from datetime import datetime
import webbrowser

tool_title = 'BUL Topo Map Inventory Tool'
map_db = db.Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/maps_we_have_test.db')

# -------------- METHODS -----------------
def multisort(elem):
    """This method is a sort key designed to be able to sort by number if elements
    are numeric strings and sort alphabetically otherwise.  Normally, numeric
    strings would be sorted like they're letters. This method also handles missing 
    values that have been filled in as '(none)' in otherwise numeric-string 
    columns, by treating them as zeroes."""

    if elem == '(none)':
         return 0
    elif is_number(elem):
        return float(elem)
    else: 
        return elem

def is_number(s):
    """Given a string s, returns true if the string is numeric and false otherwise."""
    try:
        float(s)
        return True
    except ValueError:
        return False

# dropdowns
def grab_dd_values():
    """traverses the drop-downs in order, returns a list of the selected values"""
    data = []
    for dd in dropdowns.values():
        data.append(dd.menu.get()) 
    return data

# dropdowns, label names, add1 button
def dd_selected(cur_dd: LabeledDropDownMenu): 
    """given a selection in a given drop-down menu, control configuration of other drop-downs"""
    # disable the we have 1 button by default
    add1_btn['state'] = tk.DISABLED

    # if the user has made a selection for the last drop-down in the hierarchy,
    # activate the we have 1 and we have multiple buttons and exit this method
    if cur_dd.index == len(label_names) - 1:
        add1_btn['state'] = tk.NORMAL
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

def generate_new_id():
    """reads next available ID number from a csv, writes a new number to that csv,
    and returns the next available ID number.  Used for generating unique ID 
    numbers for exception maps"""
    new_id = file_io.read_next_exception_id("next_exception_id.csv")
    file_io.write_next_exception_id("next_exception_id.csv", int(new_id) + 1)
    return new_id

# dialog, dialogContents
def remove_record(removal_id):
    """deletes a given scan id from sqlite backend"""
    table, id_name = "usgs_topos_we_have", "scan_id"
    if len(str(removal_id)) < 6:
        table, id_name = "exception_maps_we_have", "map_id"
    before = map_db.fetch(table, id_name, removal_id)
    if len(before) == 0:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Map " + str(removal_id) + " has already been removed.")
        return None
    map_db.remove(table, id_name, removal_id)
    remaining = map_db.fetch(table, id_name, removal_id)
    if len(remaining) == 0:
        # call the method to display confirmation of removal window
        dialog['foreground'] = '#0f0' # text will be green
        dialogContents.set("Map " + str(removal_id) + " successfully removed.")
    else:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Possible error removing map " + str(removal_id) + " from the database.")
    pass

#tbl
def remove(removal_id, window):
    remove_record(removal_id)
    tbl.delete(tbl.selection())
    window.destroy()

# root
def confirm_removal(removal_id):
    top = Toplevel(root)
    top.wm_transient(root)
    top.grab_set() # makes it so user can't interact with the main window while the confirm removal window is open
    top.geometry("400x250")
    top.title("Confirm removal")
    Label(top, text = "Please confirm that you want to remove map " + removal_id + ".").place(relx=0.5, rely=0.3, anchor=CENTER)
    Button(top, text= "Yes, remove this record", foreground='#f00', command=lambda:remove(removal_id, top)).place(relx=0.5, rely=0.5, anchor=CENTER)

# root
def record_exception(selected_vals):
    exc = Toplevel(root)
    exc.wm_transient(root)
    exc.grab_set() # makes it so user can't interact with the main window while exception window is open
    exc.title("Record an exception")
    content = tk.Frame(exc)
    content.grid(row=0, column=0, padx=10, pady=20)
    title = ttk.Label(content, text="Fill in as much information as possible about the map in hand.")
    title.grid(row=0, column=0, columnspan=6, rowspan=1, padx=100, pady=5)
    options = tk.Frame(content)
    options.grid(row=1, column=0, columnspan=COL_WIDTH, rowspan=8, pady=5)

    # producer radiobutton
    ttk.Label(content, text="Map producer:").grid(row=1, column=0, padx=10)
    producer = StringVar()
    producers = ['Army Map Service', 'Bureau of Land Management', 'Defense Mapping Agency', 'USGS']
    for idx, prod in enumerate(producers):
        ttk.Radiobutton(options, text=prod, variable=producer, value=prod).grid(row=idx+2, column=0, columnspan=3, pady=5, padx=10, sticky='w')

    # # labeled drop down menus for scale, state, and cell name
    ttk.Label(options, text="Map Scale:").grid(row=1, column=3, pady=5, sticky='e')
    scale_dd = ttk.Combobox(options)
    scale_dd.grid(row=1, column=4, columnspan=2, pady=5, sticky='w')
    scale_dd['values'] = sorted(list(maps.keys()), key=multisort)

    # load in information about GNIS cell IDs for given states and cells
    cells = {}
    file_io.read_gnis("usgs_topos.csv", cells)

    ttk.Label(options, text="Cell Name:").grid(row=3, column=3, pady=5, sticky='e')
    cell_dd = ttk.Combobox(options) # , state=DISABLED
    cell_dd.grid(row=3, column=4, columnspan=2, pady=5, sticky='w')

    ttk.Label(options, text="Primary State:").grid(row=2, column=3, pady=5, sticky='e')
    state_dd = ttk.Combobox(options)
    state_dd.grid(row=2, column=4, columnspan=2, pady=5, sticky='w')
    state_dd['values'] = sorted(list(cells.keys()), key=multisort)
    state_dd.bind('<<ComboboxSelected>>', lambda event, sdd=state_dd, cdd=cell_dd: state_selected(cells, sdd, cdd))

    ttk.Label(options, text="Map Year:").grid(row=4, column=3, pady=5, sticky='e')
    myr = tk.StringVar()
    map_year_entry = tk.Entry(options, textvariable=myr)
    map_year_entry.grid(row=4, column=4, columnspan=2, pady=5, sticky='w')

    ttk.Label(options, text="Print Year:").grid(row=5, column=3, pady=5, sticky='e')
    pyr = tk.StringVar()
    print_year_entry = tk.Entry(options, textvariable=pyr)
    print_year_entry.grid(row=5, column=4, columnspan=2, pady=5, sticky='w')

    for idx, option in enumerate([scale_dd, state_dd, cell_dd, myr, pyr]):
        if selected_vals[idx] != '(none)':
            option.set(selected_vals[idx])
        if idx==1 and selected_vals[idx] != '':
            state_selected(cells, state_dd, cell_dd)

        ttk.Label(options, text="Sheet:").grid(row=6, column=2, pady=5, sticky='e')
    sheet_entry = ttk.Entry(options)
    sheet_entry.grid(row=6, column=1, pady=5, sticky='w')

    ttk.Label(options, text="Series:").grid(row=6, column=0, pady=5, sticky='e')
    series_entry = ttk.Entry(options)
    series_entry.grid(row=6, column=3, pady=5, sticky='w')

    ttk.Label(options, text="Edition:").grid(row=6, column=4, pady=5, sticky='e')
    edition_entry = ttk.Entry(options)
    edition_entry.grid(row=6, column=5, pady=5, sticky='w')

    dmgvar = BooleanVar(value=False)
    damaged = Checkbutton(options, text="This map is significantly damaged", 
                variable=dmgvar, onvalue=True)
    damaged.grid(row=7, column=0, columnspan=3, rowspan=1, padx=5, pady=5)
    damaged.deselect()

    dupevar = BooleanVar(value=False)
    duplicate = Checkbutton(options, text="We have duplicate(s) for this map", 
                variable=dupevar, onvalue=True)
    duplicate.grid(row=7, column=3, columnspan=3, rowspan=1, padx=5, pady=5)
    duplicate.deselect()

    map_vars = [producer, scale_dd, state_dd, cell_dd, map_year_entry, 
        print_year_entry, sheet_entry, series_entry, edition_entry, dmgvar, dupevar]

    record_exc_btn = ttk.Button(exc, text= "Record this map", command=lambda:insert_exc(map_vars, cells, exc))
    record_exc_btn.grid(row=8, column=0, columnspan=3, pady=10)

# independent
def insert_exc(exc_map_vars, cells, window):
    map_info = [x.get() for x in exc_map_vars]
    print(map_info)
    try:
        scale = int(map_info[1])
    except ValueError:
        scale = 24000
    state = map_info[2]
    cell = map_info[3]
    closest_gnis = ''
    if state in cells:
        if cell in cells[state]:
            min_diff = float('inf') # initialize at positive infinity
            for scl, gnis in cells[state][cell]:
                if abs(int(scl) - scale) < min_diff:
                    min_diff = abs(int(scl) - scale)
                    closest_gnis = gnis
    # "(map_id, producer, map_scale, primary_state, cell_name, gnis_cell_id, date_on_map, print_year, sheet, series, edition, is_damaged, is_duplicate, recorded_by, recorded_time)"
    new_id = generate_new_id()
    exc_tbl_row = [new_id]
    exc_tbl_row.extend(map_info[:4])
    exc_tbl_row.append(closest_gnis)
    exc_tbl_row.extend(map_info[4:-2])
    exc_tbl_row.extend([int(x) for x in map_info[-2:]])
    exc_tbl_row.extend([initials.get(), int(datetime.now().strftime('%Y%m%d%H%M'))])
    print(exc_tbl_row)

    # table display row
    tbl_dsply_row = [new_id]
    tbl_dsply_row.extend(map_info[:6])
    tbl_dsply_row.extend(map_info[-2:])
    print(tbl_dsply_row)

    map_db.insert_exception(exc_tbl_row)
    inserted = map_db.fetch("exception_maps_we_have", "map_id", new_id)
    if len(inserted) == 1:
        tbl.insert('', 0, values=tbl_dsply_row) # display record on table, as well as confirmation
        dialog['foreground'] = '#0f0' # text will be green
        dialogContents.set("Map " + str(new_id) + " successfully recorded!")
        dmgvar.set(False)
        dupevar.set(False)

    window.destroy() # close the exception window

# independent
def state_selected(cells, state_dd, cell_dd):
    cell_dd['values'] = sorted(list(cells[state_dd.get()].keys()), key=multisort)
    cell_dd.set('')

# map_db / dialog / dialogContents / dmg / dupe
def insert_exception(scan_id):
    """inserts record for map we have on hand into sqlite backend, confirms the
    insertion by selecting that record from the db, and then calls methods to add
    that record to the table frame and print out a message, etc"""
    # maybe insert, then fetch for confirmation?
    before = map_db.fetch("usgs_topos_we_have", "scan_id", scan_id)
    if len(before) > 0:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Map " + str(scan_id) + " has already been recorded.")
        return None
    map_db.insert_topo(scan_id
                , initials.get() # recorded_by
                , int(datetime.now().strftime('%Y%m%d%H%M')) # recorded_time
                , int(dmgvar.get()) # is_damaged (0 or 1)
                , int(dupevar.get())) # is_duplicate (0 or 1)
    inserted = map_db.fetch("usgs_topos_we_have", "scan_id", scan_id)
    if len(inserted) == 1:
        add_to_table(scan_id) # display record on table, as well as confirmation
        dialog['foreground'] = '#0f0' # text will be green
        dialogContents.set("Map " + str(scan_id) + " successfully recorded!")
        dmgvar.set(False)
        dupevar.set(False)

    else:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Possible error inserting map " + str(scan_id) + " into the database.")

# dialog / dialogContents 
def remove_selected_record():
    """
    Defines action that's taken when the Remove selected record button is pressed
    """
    selected = tbl.selection()
    if len(selected) == 1:
        confirm_removal(tbl.item(selected, 'values')[0]) # open confirmation window
    elif len(selected) == 0:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Nothing is selected.  Click on a row in the table to select it.")
    else: # if more than 1 item from the table is selected when the Remove button is pressed
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Cannot remove more than one record at a time.")

# dropdowns
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
        select_from_multiple(results)

# independent
def select_from_multiple(results):
    """create the pop-up window where the user chooses which map record matches
    the map physically in hand by opening up the links to the different options"""
    win = Toplevel(root)
    win.wm_transient(root)
    win.title("Multiple matches found")
    ttk.Label(win, text="The USGS database has multiple records for that map.  Please select the record that matches the map in hand.").grid(row=0, columnspan=2, pady=20, padx=20)
    choices = StringVar()
    record_btn = Button(win, text="Record this map", command=lambda: record_this_map(choices.get(), win), state=DISABLED)

    for idx, result in enumerate(results):
        result_id = result[0]
        result_link=result[1]
        ttk.Radiobutton(win, text=result_id, variable=choices, command=lambda:record_btn.configure(state=NORMAL), value=result_id).grid(row=idx+1, column=0, pady=5, sticky='e')
        Button(win, text="Open pdf in browser", command=lambda result_link=result_link: webbrowser.open_new_tab(result_link)).grid(row=idx+1, column=1, sticky='w')
    
    record_btn.grid(row=idx+2, column=0, columnspan=2, pady=20)

# independent
def record_this_map(scan_id, window):
    insert_record(scan_id)
    window.destroy()

# map_db / dialog / dialogContents / dmg / dupe
def insert_record(scan_id):
    """inserts record for map we have on hand into sqlite backend, confirms the
    insertion by selecting that record from the db, and then calls methods to add
    that record to the table frame and print out a message, etc"""
    # maybe insert, then fetch for confirmation?
    before = map_db.fetch("usgs_topos_we_have", "scan_id", scan_id)
    if len(before) > 0:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Map " + str(scan_id) + " has already been recorded.")
        return None
    map_db.insert_topo(scan_id
                , initials.get() # recorded_by
                , int(datetime.now().strftime('%Y%m%d%H%M')) # recorded_time
                , int(dmgvar.get()) # is_damaged (0 or 1)
                , int(dupevar.get()) # is_duplicate (0 or 1)
                , 'USGS') # producer
    inserted = map_db.fetch("usgs_topos_we_have", "scan_id", scan_id)
    if len(inserted) == 1:
        add_to_table(scan_id) # display record on table, as well as confirmation
        dialog['foreground'] = '#0f0' # text will be green
        dialogContents.set("Map " + str(scan_id) + " successfully recorded!")
        dmgvar.set(False)
        dupevar.set(False)

    else:
        dialog['foreground'] = '#f00' # text will be red
        dialogContents.set("Possible error inserting map " + str(scan_id) + " into the database.")

# tbl
def add_to_table(scan_id):
    """insert info about a map we have into the display table"""
    tbl_vals = [scan_id, 'USGS'] 
    tbl_vals.extend(grab_dd_values())
    # replace 'no' with dupe_var once created 
    tbl_vals.extend([dmgvar.get(), dupevar.get()])
    tbl.insert('', 0, values=tbl_vals)
    # ('Scan ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year', 'Damaged', 'Duplicate')

# dropdowns, exc button, rmv button / dialog / dialogContents / initials
def sign_in(event):
    """selection is made on the initials drop down"""

    # # This if-block supports users typing in their own initials, by updating the csv file of users with the new initials
    # if initials.get() not in initials['values']: # if someone types in a new username
    #     # add their entry to the drop-down of possible values
    #     initials['values'] = (*initials['values'], initials.get())
    #     # and save the new set of possible values to users.csv
    #     file_io.write_users('users.csv', initials['values'])

    list(dropdowns.values())[0].enable() # enable the first drop-down menu
    exception_btn['state'] = NORMAL
    remove_btn['state'] = NORMAL

    # print a confirmation for sign-in
    dialog['foreground'] = '#0f0' # text will be green
    dialogContents.set("Welcome, " + initials.get() + "!")

    # also, call the method to update table with that person's stuff
    populate_most_recent(initials.get())

# tbl / map_db
def populate_most_recent(initials):
    # clear whatever's currently in the table
    for item in tbl.get_children():
        tbl.delete(item)
    
    # grab the most recent maps recorded by the given initials, add them to table
    rows = map_db.fetch_most_recent('usgs_topos_we_have', 'scan_id', initials)
    exc_rows = map_db.fetch_most_recent('exception_maps_we_have', 'map_id', initials)
    rows.extend(exc_rows)
    most_recent = sorted(rows, key=lambda lst: int(lst[-1]))
    for row in most_recent[-10:]:
        tbl_row = ["(none)" if val is None or val == '' else val for val in row[:-3]] # convert empty values from database to (none) in table
        tbl_row.extend([bool(val) for val in row[-3:-1]]) # convert 1s and 0s from is_damaged and is_duplicate columns to True and False for table
        tbl.insert('', 0, values=tbl_row)

COL_WIDTH = 7

# ------------------- initialize tkinter window -----------------

root = tk.Tk()
root.title(tool_title)

# Frame containing the entire window - exists in order to customize margins
content = tk.Frame(root)
content.grid(row=0, column=0, padx=10, pady=20)

# add a header frame with a title and a drop-down menu for users to sign in
header = tk.Frame(content)
title = ttk.Label(header, text=tool_title)
sign_in_label = ttk.Label(header, text="Select your initials to sign in:")
initials = ttk.Combobox(header, state='readonly', values=file_io.read_users('users.csv'))
initials.bind('<<ComboboxSelected>>', sign_in)

# add an options frame to contain all the menus and buttons for recording maps
options = tk.Frame(content)

# set up a series of labeled drop down menus for a list of attributes, and put 
# those LDDMs into an ordered dictionary structure so that they can be looked up
# by name but also be stored in a specific order
label_names = ['Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year'] 
dropdowns = OrderedDict()

for idx, lbl in enumerate(label_names):
    dropdowns[lbl] = LabeledDropDownMenu(ttk.Label(options, text=lbl + ": ")
        , ttk.Combobox(options, state=DISABLED)
        , ttk.Button(options, text="^", state=DISABLED)
        , ttk.Button(options, text="v", state=DISABLED)
        , idx
        , {}
    )
# for example, dropdowns['Cell Name'].menu['state'] = 'readonly' would activate the Cell Name drop down menu.

# read map data into a nested dictionary
maps = {}
file_io.read_topos('usgs_topos.csv', maps)

# initialize the first dropdown
first_dd = list(dropdowns.values())[0] # access the first labeled dropdown menu
first_dd.next_vals = maps
first_dd.menu['values'] = sorted(list(maps.keys()), key=multisort) # or whatever corresponding dict's keys
# first_dd['state'] = 'readonly'

# bind each dropdown to dd_selected with itself as an argument, and each prev or
# next button to the prev and next button methods with each dd as an argument.
# The dd=dd statements are necessary - without them, the lambda would point to the 
# variable dd at the end of the for loop rather than its value at each iteration.
for dd in list(dropdowns.values()):
    dd.menu.bind('<<ComboboxSelected>>', lambda event, dd=dd: dd_selected(dd))
    dd.prev.configure(command = lambda dd=dd: prev_button(dd))
    dd.next.configure(command = lambda dd=dd: next_button(dd))  

dmgvar = BooleanVar(value=False)
damaged = ttk.Checkbutton(options, text="This map is significantly damaged", 
            variable=dmgvar, onvalue=True)

dupevar = BooleanVar(value=False)
duplicate = ttk.Checkbutton(options, text="We have duplicate(s) for this map", 
            variable=dupevar, onvalue=True)

exception_btn = ttk.Button(options, text='Record an exception', command=lambda: record_exception(grab_dd_values()), state=DISABLED)

remove_btn = ttk.Button(options, text='Remove selected record', command=remove_selected_record, state=DISABLED)

add1_btn = ttk.Button(options, text='Record this map', command=we_have_1, state=DISABLED)

dialogContents = StringVar()
dialog = ttk.Label(options)
dialog['textvariable'] = dialogContents
dialog.grid(row=8, column=3, columnspan=3, rowspan=1, pady=5, sticky='s')

# ---------------- table frame ---------------------------
table = tk.Frame(content)

tbl_cols = ('Map ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year', 'Damaged', 'Duplicate')
tbl = ttk.Treeview(table, columns=tbl_cols, show='headings')

# define headings
for col in tbl_cols:
    tbl.heading(col, text=col)
    tbl.column(col, width=100)
# add a scrollbar
tbl_scroll = ttk.Scrollbar(table, orient=tk.VERTICAL, command=tbl.yview)
tbl.configure(yscroll=tbl_scroll.set)

# -------------------- place widgets onto the main window -------------------

# ---- header frame ----
header.grid(row=0, column=0, columnspan=COL_WIDTH, rowspan=1, pady=5)
title.grid(row=0, column=0, columnspan=5, rowspan=1, padx=100, pady=5)
sign_in_label.grid(row=0, column=5)
initials.grid(row=0, column=6, padx=20)

# ---- options frame ----
options.grid(row=1, column=0, columnspan=COL_WIDTH, rowspan=8, pady=5)

for idx, dd in enumerate(dropdowns.values()):
    r = (idx%3)*2 + 1  # creates three rows of drop downs, starting at row 1, with
    c = int(idx/3)*3   # as many columns as are needed for the set of drop downs

    # place each label on the left, then the menu, then the prev/next buttons
    dd.label.grid(row=r, column=c, rowspan=2, padx=20, pady=10, sticky='e')
    dd.menu.grid(row=r, column=c+1, rowspan=2, padx=10)
    dd.prev.grid(row=r, column=c+2, sticky='w')
    dd.next.grid(row=r+1, column=c+2, sticky='w')

damaged.grid(row=5, column=3, columnspan=3, rowspan=1) # dmg checkbox
duplicate.grid(row=6, column=3, columnspan=3, rowspan=1) # duplicate checkbox
exception_btn.grid(row=7, column=0, columnspan=3, pady=5) # record exception button
remove_btn.grid(row=8, column=0, columnspan=3, pady=5) # remove selected button
add1_btn.grid(row=7, column=3, rowspan=2, columnspan=3, pady=5) # record this map button
dialog.grid(row=8, column=3, columnspan=3, rowspan=1, pady=5) # dialog label

# ---- table frame ----
table.grid(row=9, column=0, columnspan=7, rowspan=1, pady=5)
tbl.grid(row=9, column=0, columnspan=6, rowspan=1) # table 
tbl_scroll.grid(row=9, column=6, rowspan=1, sticky='ns') # table scroll bar

# ------------------------------ run the app -------------------------------
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