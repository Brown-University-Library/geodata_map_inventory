# Ethan McIntosh - GIS and Data Services - Brown University - August 2022

import tkinter as tk
from tkinter import ttk
import webbrowser
from datetime import datetime
import file_io, db # import the other files in this package

tool_title = 'BUL Topo Map Inventory Tool'
map_db = db.Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/bul_topo_map_inventory.db')

# ------------------------------------------------------------------------------
# ---------------------------- CUSTOM CLASSES ----------------------------------
# ------------------------------------------------------------------------------

class AutocompleteCombobox(ttk.Combobox):
    """
    The code for this class is an extension of the tkinter combobox (drop-down menu) 
    which autocompletes typed-in entries according to a set of predefined values. 
    I modified the original authors' code slightly in order to have autocompletion 
    trigger other functions under certain conditions. The doc-string comments for 
    each method are mine, but the in-line comments are by the original authors.

    Original author information:
        Created by Mitja Martini on 2008-11-29.
        Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
        Licensed same as original (not specified?), or public domain, whichever is less restrictive.

    Source: https://mail.python.org/pipermail/tkinter-discuss/2012-January/003041.html
    """
    def set_completion_list(self, completion_list, select_func=lambda:None, no_match_func=lambda:None):
            """This initializes the drop-down menu with some extra data structures that
            are needed for the autocomplete to be functional. The optional select_func 
            and no_match_func arguments allow you to specify functions that should be
            called when an autocomplete is performed (select_func) or when a typed entry
            does not match the predefined list of options (no_match_func)"""
            self._completion_list = completion_list
            self._hits = []
            self._hit_index = 0
            self.position = 0
            self.bind('<KeyRelease>', self.handle_keyrelease)
            self['values'] = self._completion_list  # Setup our popup menu
            self.select_func = select_func
            self.no_match_func = no_match_func

    def autocomplete(self, delta=0):
            """This method is called in response to keystrokes in order to autocomplete the Combobox.
            If an autocomplete is performed, call the given select_func().
            If the value in the menu doesn't match a predefined option, call the given no_match_func()."""
            if delta: # need to delete selection otherwise we would fix the current position
                    self.delete(self.position, tk.END)
            else: # set position to end so selection starts where textentry ended
                    self.position = len(self.get())
            # collect hits
            _hits = []
            for element in self._completion_list:
                    if element.lower().startswith(self.get().lower()): # Match case insensitively
                            _hits.append(element)
            # if we have a new hit list, keep this in mind
            if _hits != self._hits:
                    self._hit_index = 0
                    self._hits=_hits
            # only allow cycling if we are in a known hit list
            if _hits == self._hits and self._hits:
                    self._hit_index = (self._hit_index + delta) % len(self._hits)
            # now finally perform the auto completion
            if self._hits:
                    self.delete(0,tk.END)
                    self.insert(0,self._hits[self._hit_index])
                    self.select_range(self.position,tk.END)
                    self.select_func()
            else: # if whatever is typed into the box does not match a predefined option
                self.no_match_func()

    def handle_keyrelease(self, event):
            """event handler for the keyrelease event while this widget is active
            If the value in the menu doesn't match a predefined option, call the given no_match_func()
            If it does match a predefined option, call the given select_func()"""
            if event.keysym == "BackSpace":
                    self.delete(self.index(tk.INSERT), tk.END)
                    self.position = self.index(tk.END)
                    if self.get() not in self._completion_list:
                        self.no_match_func()
                    else:
                        self.select_func()
            if event.keysym == "Left":
                    if self.position < self.index(tk.END): # delete the selection
                            self.delete(self.position, tk.END)
                    else:
                            self.position = self.position-1 # delete one character
                            self.delete(self.position, tk.END)
            if event.keysym == "Right":
                    self.position = self.index(tk.END) # go to end (no selection)
            if len(event.keysym) == 1:
                    self.autocomplete()
            # No need for up/down, we'll jump to the popup
            # list at the position of the autocompletion

class LabeledDropDownMenu:
    """This class is meant to bundle drop-down menus with other tkinter widgets and with 
    associated data into a single object. This bundling makes it easier to have a 
    series of drop-down menus that trigger actions on each other in response to 
    selections, and which can each have their own previous and next buttons.
    """
    def __init__(self, label: tk.Label, menu: AutocompleteCombobox, prev: tk.Button, 
                next: tk.Button, index: int, next_vals: dict):
        """Initialize the tkinter widgets (label, menu, prev, next) and associated
        data like index (the position of this drop-down menu in the hierarchy) and 
        next_vals (a dictionary whose keys are the possible values of the menu).
        """
        self.label = label
        self.menu = menu
        self.menu.bind('<<ComboboxSelected>>', lambda event: self.dd_selected())
        self.index = index
        self.prev = prev
        self.prev.configure(command = lambda: self.prev_button())
        self.next = next
        self.next.configure(command = lambda: self.next_button()) 
        self.next_vals = next_vals
        self.next_lddm = None

    def set_next_lddm(self, next_lddm):
        self.next_lddm = next_lddm

    def disable(self):
        """disables the drop-down menu and its associated prev/next buttons"""
        self.menu['state'] = tk.DISABLED
        self.prev['state'] = tk.DISABLED
        self.next['state'] = tk.DISABLED

    def enable(self):
        """enables the drop-down menu and its associated prev/next buttons"""
        self.menu['state'] = tk.NORMAL
        self.prev['state'] = tk.NORMAL
        self.next['state'] = tk.NORMAL

    def prev_button(self):
        """In response to clicking the prev button, toggle the value on the given
        drop-down menu to its previous possible value."""
        val = self.menu.current()
        if val > 0: # if we're not at the beginning of the list of possible values,
            # set the drop down to the next value in the list of possible values
            self.menu.current(val - 1) 
            self.dd_selected()

    def next_button(self):
        """In response to clicking the prev button, toggle the value on the given
        drop-down menu to its next possible value."""
        val = self.menu.current()
        if val != len(self.menu['values']) - 1: # if we're not at the end of the list of possible values,
            # set the drop down to the next value in the list of possible values
            self.menu.current(val + 1) 
            self.dd_selected()

    def disable_next(self):
        """Disable the next drop-down menu within the dropdowns hierarchy, as well
        as all other menus after the next one. If we're on the last menu, disable 
        the "record this map" button on the main window instead.
        """
        if self.index < len(dropdowns) - 1:
            self.next_lddm.disable()
            self.next_lddm.menu.set('')
            self.next_lddm.disable_next()
        else:
            add1_btn['state'] = tk.DISABLED

    def dd_selected(self): 
        """This method is called whenever a value is selected in a given drop-down menu.
        For example, if a map scale is selected, the possible values of the primary 
        state drop-down are updated to only show states for which maps were produced
        at the given scale, the primary state drop-down is activated, and all of the drop-down 
        menus after primary state are deactivated.  If there's only one state for a given 
        map scale, that state will be "locked in" and dd_selected will be called on the 
        state drop-down in order to update the values of the cell name drop-down."""
        # disable the "record this map" button by default
        add1_btn['state'] = tk.DISABLED

        # if the user has made a selection for the last drop-down in the hierarchy,
        # activate the "record this map" button and exit this method
        if self.index == len(label_names) - 1:
            add1_btn['state'] = tk.NORMAL
            return None # exit this method, do not proceed to the remaining lines of code

        # otherwise (if the selection is for some other drop-down), we want to alter
        # the possible values of the next drop down menu in the hierarchy
        next_dd = self.next_lddm
        next_dd.next_vals = self.next_vals[self.menu.get()]
        vals = sorted(list(next_dd.next_vals.keys()), key=multisort)
        # next_dd.menu['values'] = vals
        next_dd.menu.set_completion_list(vals, lambda: next_dd.dd_selected(), lambda: next_dd.disable_next())
        
        # blank out & disable all drop-down menus after whichever one was selected
        # so that selections high in the hierarchy will clear out the following menus' values
        # for dd in list(dropdowns.values())[next_dd.index:]: 
        #     dd.menu.set('')
        #     dd.disable()
        next_dd.disable_next()

        if len(vals) == 1:  # if there's only 1 possible value for the next drop down
            # lock that value into that drop-down menu and disable it from selections
            next_dd.menu.set(vals[0])
            next_dd.disable()
            # then, do what needs to be done in response to the next dd being selected
            next_dd.dd_selected()
        else: # if there are more than 1 possible values for the next drop down
            # activate the next drop down so the user can make a selection on it
            next_dd.enable()  

# ------------------------------------------------------------------------------
# ------------------------ INITIALIZATION METHODS ------------------------------
# ------------------------------------------------------------------------------

def sign_in(event):
    """Defines what happens when the user selects their initials from the sign-in
    menu. The first drop-down menu, the exception button, and the remove selected 
    record button are activated, a welcome message is displayed, and populate_most_recent()
    is called to display the map records most recently inventoried by the selected user."""

    dropdowns[0].enable()
    exception_btn['state'] = tk.NORMAL
    remove_btn['state'] = tk.NORMAL
    dialog['foreground'] = '#0f0' # text will be green
    dialogContents.set("Welcome, " + initials.get() + "!")
    populate_most_recent(initials.get())

def populate_most_recent(initials):
    """Updates the table display to show the most recent 10 map records inventoried by the given user."""
    # clear whatever's currently in the table
    for item in tbl.get_children():
        tbl.delete(item)
    
    # grab data on the most recent maps recorded by the given initials
    rows = map_db.fetch_most_recent('usgs_topos_we_have', 'scan_id', initials)
    exc_rows = map_db.fetch_most_recent('exception_maps_we_have', 'map_id', initials)
    rows.extend(exc_rows)
    # sort the most recent regular maps together with the most recent exceptions
    most_recent = sorted(rows, key=lambda lst: int(lst[-1])) 

    # add the 10 most recent rows to the table display
    for row in most_recent[-10:]:
        # convert empty values from database to (none) in table display
        tbl_row = ["(none)" if val is None or val == '' else val for val in row[:-3]] 
        # convert 1s and 0s from is_damaged and is_duplicate columns in database to read as True and False in table display
        tbl_row.extend([bool(val) for val in row[-3:-1]]) 
        tbl.insert('', 0, values=tbl_row)

# ------------------------------------------------------------------------------
# -------------------------- RECORDING MAPS METHODS ----------------------------
# ------------------------------------------------------------------------------

def record_this_map():
    """
    When the "Record this map" button is pressed on the main window, the result
    values (the scan IDs and product URLs of matching map(s)) are extracted from 
    the next_vals field of the last LDDM. If there's only one result, those values 
    are inserted into the database. Otherwise, we call select_from_multiple().
    """
    last_dd = dropdowns[len(dropdowns)-1]
    results = last_dd.next_vals[last_dd.menu.get()] # should be a list of tuples
    if len(results) == 1:
        insert_record(results[0][0])  # passing in just the scan ID
    else:
        select_from_multiple(results)

def select_from_multiple(results):
    """Creates a pop-up window where the user chooses which of the multiple resulting
    map records matches the map physically in hand. Each map is an option on a 
    radiobutton, and each option has a button which will open up the map pdf in 
    the user's web browser.  by opening up the links to the different options"""
    win = tk.Toplevel(root)
    win.wm_transient(root)
    win.title("Multiple matches found")
    ttk.Label(win, text="The USGS database has multiple records for that map.  Please select the record that matches the map in hand.")\
        .grid(row=0, columnspan=2, pady=20, padx=20)
    choices = tk.StringVar()
    record_btn = tk.Button(win, text="Record this map", command=lambda: record_chosen_map(choices.get(), win), state=tk.DISABLED)

    for idx, result in enumerate(results):
        result_id = result[0]
        result_link=result[1]
        ttk.Radiobutton(win, text=result_id, variable=choices, command=lambda:record_btn.configure(state=tk.NORMAL), value=result_id)\
            .grid(row=idx+1, column=0, pady=5, sticky='e')
        tk.Button(win, text="Open pdf in browser", command=lambda result_link=result_link: webbrowser.open_new_tab(result_link))\
            .grid(row=idx+1, column=1, sticky='w')
    
    record_btn.grid(row=idx+2, column=0, columnspan=2, pady=20)

def record_chosen_map(scan_id, window):
    """When the user clicks on the button on the multiple matches window to record
    a given map, that map is inserted into the database using its ID and the pop-up
    window is closed."""
    insert_record(scan_id)
    window.destroy()

def insert_record(scan_id):
    """Inserts record for map we have on hand into sqlite backend by grabbing map
    information from the main window drop-down menus and checkboxes, confirms the
    insertion by selecting that record from the db, and then calls methods to add
    that record to the table display and print out a confirmation message.
    """
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

def add_to_table(scan_id):
    """Given the ID of a map, insert information about a map (whatever is currently
    selected in the drop-down menus and checkboxes) into the table display (tbl)"""
    tbl_vals = [scan_id, 'USGS'] 
    tbl_vals.extend(grab_dd_values())
    tbl_vals.extend([dmgvar.get(), dupevar.get()])
    tbl.insert('', 0, values=tbl_vals)
    # below are the columns that will be in the table display:
    # ('Scan ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year', 'Damaged', 'Duplicate')

def grab_dd_values():
    """traverses the drop-downs in order, returns a list of their currently selected values"""
    data = []
    for dd in dropdowns:
        data.append(dd.menu.get()) 
    return data

# ------------------------------------------------------------------------------
# ----------------------- EXCEPTION-RECORDING METHODS --------------------------
# ------------------------------------------------------------------------------

def record_exception(selected_vals):
    """When the "Record an exception" button is pressed, create a new window where
    users have more flexibility in recording map attributes. Attributes from the root
    window that had been selected when the button was hit (selected vals) are "pre-loaded" 
    into the exception window for convenience. With exception maps, the only thing we 
    want to record besides what the user enters is the GNIS cell ID of the exception
    map's cell name, if it uses the same cell system as USGS. Therefore, we also read
    in data on GNIS cell IDs by state and cell and populate menu values accordingly.
    """
    exc = tk.Toplevel(root)
    exc.wm_transient(root) # makes the exception window a sub-window rather than a separate window
    exc.grab_set() # makes it so user can't interact with the main window while exception window is open
    exc.title("Record an exception")
    content = tk.Frame(exc)
    content.grid(row=0, column=0, padx=10, pady=20)
    title = ttk.Label(content, text="Fill in as much information as possible about the map in hand.")
    title.grid(row=0, column=0, columnspan=6, rowspan=1, padx=100, pady=5)
    options = tk.Frame(content)
    options.grid(row=1, column=0, columnspan=7, rowspan=8, pady=5)

    # producer radiobutton
    ttk.Label(content, text="Map producer:").grid(row=1, column=0, padx=10)
    producer = tk.StringVar()
    producers = ['Army Map Service', 'Bureau of Land Management', 'Defense Mapping Agency', 'USGS']
    for idx, prod in enumerate(producers):
        ttk.Radiobutton(options, text=prod, variable=producer, value=prod)\
            .grid(row=idx+2, column=0, columnspan=3, pady=5, padx=10, sticky='w')

    # # labeled drop down menus for scale, state, and cell name
    ttk.Label(options, text="Map Scale:").grid(row=1, column=3, pady=5, sticky='e')
    scale_dd = AutocompleteCombobox(options)
    scale_dd.grid(row=1, column=4, columnspan=2, pady=5, sticky='w')
    scale_dd.set_completion_list(sorted(list(maps.keys()), key=multisort))

    # load in information about GNIS cell IDs for given states and cells
    cells = {}
    file_io.read_gnis("usgs_topos.csv", cells)

    ttk.Label(options, text="Cell Name:").grid(row=3, column=3, pady=5, sticky='e')
    cell_dd = AutocompleteCombobox(options, state=tk.NORMAL) # , state=DISABLED
    cell_dd.grid(row=3, column=4, columnspan=2, pady=5, sticky='w')

    ttk.Label(options, text="Primary State:").grid(row=2, column=3, pady=5, sticky='e')
    state_dd = AutocompleteCombobox(options)
    state_dd.grid(row=2, column=4, columnspan=2, pady=5, sticky='w')
    state_dd.set_completion_list(sorted(list(cells.keys()), key=multisort), lambda: state_selected(cells, state_dd, cell_dd))
    state_dd.bind('<<ComboboxSelected>>', lambda event, sdd=state_dd, cdd=cell_dd: state_selected(cells, sdd, cdd))

    ttk.Label(options, text="Map Year:").grid(row=4, column=3, pady=5, sticky='e')
    myr = tk.StringVar()
    map_year_entry = tk.Entry(options, textvariable=myr)
    map_year_entry.grid(row=4, column=4, columnspan=2, pady=5, sticky='w')

    ttk.Label(options, text="Print Year:").grid(row=5, column=3, pady=5, sticky='e')
    pyr = tk.StringVar()
    print_year_entry = tk.Entry(options, textvariable=pyr)
    print_year_entry.grid(row=5, column=4, columnspan=2, pady=5, sticky='w')

    # now that the menus are set up, pre-load them with the main window's selected values
    for idx, option in enumerate([scale_dd, state_dd, cell_dd, myr, pyr]):
        if selected_vals[idx] != '(none)':
            option.set(selected_vals[idx])
        if idx==1 and selected_vals[idx] != '': # if the primary state menu has been pre-loaded,
            state_selected(cells, state_dd, cell_dd) # update the cells menu accordingly

    # the exception menu has several extra text entry fields to allow us to record
    # the Sheet, Series, and Edition of Army Mapping Service maps that we have
    ttk.Label(options, text="Sheet:").grid(row=6, column=2, pady=5, sticky='e')
    sheet_entry = ttk.Entry(options)
    sheet_entry.grid(row=6, column=1, pady=5, sticky='w')

    ttk.Label(options, text="Series:").grid(row=6, column=0, pady=5, sticky='e')
    series_entry = ttk.Entry(options)
    series_entry.grid(row=6, column=3, pady=5, sticky='w')

    ttk.Label(options, text="Edition:").grid(row=6, column=4, pady=5, sticky='e')
    edition_entry = ttk.Entry(options)
    edition_entry.grid(row=6, column=5, pady=5, sticky='w')

    # just like the main window, we have checkboxes to flag damages or duplicates
    dmgvar = tk.BooleanVar(value=False)
    damaged = tk.Checkbutton(options, text="This map is significantly damaged", 
                variable=dmgvar, onvalue=True)
    damaged.grid(row=7, column=0, columnspan=3, rowspan=1, padx=5, pady=5)
    damaged.deselect()

    dupevar = tk.BooleanVar(value=False)
    duplicate = tk.Checkbutton(options, text="We have duplicate(s) for this map", 
                variable=dupevar, onvalue=True)
    duplicate.grid(row=7, column=3, columnspan=3, rowspan=1, padx=5, pady=5)
    duplicate.deselect()

    map_vars = [producer, scale_dd, state_dd, cell_dd, map_year_entry, 
        print_year_entry, sheet_entry, series_entry, edition_entry, dmgvar, dupevar]

    record_exc_btn = ttk.Button(exc, text= "Record this map", command=lambda:insert_exception(map_vars, cells, exc))
    record_exc_btn.grid(row=8, column=0, columnspan=3, pady=10)

def insert_exception(exc_map_vars, cells, window):
    """When the user hits the "Record this map" button on the exceptions window,
    we first identify the GNIS cell ID of the exception map, if applicable. Then
    we insert information about the exception map into both the table display 
    and the SQLite database. Then, we close out the exceptions window.
    """
    # extract whatever values on the exception window were selected/typed in
    map_info = [x.get() for x in exc_map_vars]

    # identify the GNIS cell ID based on the selected state and cell, and then 
    # instead of looking for an exact match for map scale, we look for the GNIS
    # cell ID with the closest map scale to whatever scale was selected/typed in
    try:
        scale = int(map_info[1])
    except ValueError: # if the scale was left blank or otherwise isn't an integer,
        scale = 24000 # assign 24000 as a default for the purposes of assigning a GNIS cell ID
    state = map_info[2]
    cell = map_info[3]
    closest_gnis = ''
    if state in cells:
        if cell in cells[state]:
            # to find the closest GNIS cell ID, find the map scale with the smallest
            # difference between it and the selected map scale, and use that GNIS ID
            min_diff = float('inf')
            for scl, gnis in cells[state][cell]:
                if abs(int(scl) - scale) < min_diff:
                    min_diff = abs(int(scl) - scale)
                    closest_gnis = gnis

    # assemble the row (list of values) that will be inserted into the exception maps database table
    # Columns are map_id, producer, map_scale, primary_state, cell_name, gnis_cell_id, date_on_map, 
    # print_year, sheet, series, edition, is_damaged, is_duplicate, recorded_by, recorded_time"
    new_id = generate_new_exception_id()
    exc_tbl_row = [new_id]
    exc_tbl_row.extend(map_info[:4])
    exc_tbl_row.append(closest_gnis)
    exc_tbl_row.extend(map_info[4:-2])
    exc_tbl_row.extend([int(x) for x in map_info[-2:]])
    exc_tbl_row.extend([initials.get(), int(datetime.now().strftime('%Y%m%d%H%M'))])

    # assemble the row (list of values) that will be inserted into the table display
    # Columns are 'Scan ID', 'Producer', 'Map Scale', 'Primary State', 'Cell Name', 
    # 'Map Year', 'Print Year', 'Damaged', 'Duplicate')
    tbl_dsply_row = [new_id]
    tbl_dsply_row.extend(map_info[:6])
    tbl_dsply_row.extend(map_info[-2:])

    map_db.insert_exception(exc_tbl_row) # insert record into exception maps database table
    inserted = map_db.fetch("exception_maps_we_have", "map_id", new_id)
    if len(inserted) == 1: # if the database row insert was successful,
        tbl.insert('', 0, values=tbl_dsply_row) # display record on table, 
        dialog['foreground'] = '#0f0' # and show a confirmation in green text
        dialogContents.set("Map " + str(new_id) + " successfully recorded!")
        # we reset the damage and duplicate checkboxes to be unchecked after every map
        dmgvar.set(False)
        dupevar.set(False)

    window.destroy() # close the exception window

def generate_new_exception_id():
    """reads next available exception ID number from a csv, writes a new number
    to that csv, and returns the next available ID number. This is used to assign 
    unique ID numbers to exception maps.
    """
    new_id = file_io.read_next_exception_id("next_exception_id.csv")
    file_io.write_next_exception_id("next_exception_id.csv", int(new_id) + 1)
    return new_id

def state_selected(cells, state_dd, cell_dd):
    """On the exception window, when a selection is made on the primary state drop-down 
    menu, we want the values of the cell drop-down menu to be updated in response.
    """
    # cell_dd['values'] = sorted(list(cells[state_dd.get()].keys()), key=multisort)
    cell_dd.set_completion_list(sorted(list(cells[state_dd.get()].keys()), key=multisort))
    cell_dd.set('')

# ------------------------------------------------------------------------------
# ------------------------- REMOVING RECORDS METHODS ---------------------------
# ------------------------------------------------------------------------------

def remove_selected_record():
    """This method is what's executed when the "Remove selected record" button is pressed.
    It checks that exactly 1 table record is selected. If so, it calls confirm_removal(). 
    If not, it gives the user an informative message through the dialog label.
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

def confirm_removal(removal_id):
    """
    To confirm the removal of a selected map from the table display, a new pop-up
    window is created requiring the user to click an extra button to confirm.
    """
    top = tk.Toplevel(root)
    top.wm_transient(root)
    top.grab_set() # makes it so user can't interact with the main window while the confirm removal window is open
    top.geometry("400x250")
    top.title("Confirm removal")
    tk.Label(top, text = "Please confirm that you want to remove map " + removal_id + ".")\
        .place(relx=0.5, rely=0.3, anchor=tk.CENTER)
    tk.Button(top, text= "Yes, remove this record", foreground='#f00', command=lambda:remove(removal_id, top))\
        .place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
def remove(removal_id, window):
    """When the user confirms that they want to remove a given map from our records,
    this method activates. It deletes the selected record from tbl, closes the extra pop-up window, 
    and calls remove_record with the selected record's map ID to remove it from the database.
    """
    remove_record(removal_id)
    tbl.delete(tbl.selection())
    window.destroy()

def remove_record(removal_id):
    """Deletes the record corresponding with a given map ID from the SQLite database.
    The number of digits in the map ID determines whether it's a regular topo or
    an exception map, which determines which table to delete the record from.
    This method also verifies that after removal, there are no more maps with the 
    removed ID in the database, and prints informative messages in case of issues.
    """
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

# ------------------------------------------------------------------------------
# ------------------------ MISCELLANEOUS METHODS -------------------------------
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# -------------------------- BUILD THE MAIN WINDOW -----------------------------
# ------------------------------------------------------------------------------

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

# set up an ordered list of labeled drop down menus, one for each map attribute
label_names = ['Map Scale', 'Primary State', 'Cell Name', 'Map Year', 'Print Year'] 
dropdowns = []

for idx, lbl in enumerate(label_names):
    lddm = LabeledDropDownMenu(ttk.Label(options, text=lbl + ": ")
        , AutocompleteCombobox(options, state=tk.DISABLED)
        , ttk.Button(options, text="^", state=tk.DISABLED)
        , ttk.Button(options, text="v", state=tk.DISABLED)
        , idx
        , {}
    )
    dropdowns.append(lddm)
    if idx != 0:
        dropdowns[idx-1].set_next_lddm(lddm)

# read map data into a nested dictionary, ordered according to our set of map attributes
maps = {}
file_io.read_topos('usgs_topos.csv', maps)

# initialize the first dropdown
first_dd = dropdowns[0] # access the first labeled dropdown menu
first_dd.next_vals = maps # give the map data to the first menu
first_dd.menu.set_completion_list(sorted(list(maps.keys()), key=multisort), \
    lambda: first_dd.dd_selected(), lambda: first_dd.disable_next())

# checkboxes to flag damages and duplicates
dmgvar = tk.BooleanVar(value=False)
damaged = ttk.Checkbutton(options, text="This map is significantly damaged", 
            variable=dmgvar, onvalue=True)

dupevar = tk.BooleanVar(value=False)
duplicate = ttk.Checkbutton(options, text="We have duplicate(s) for this map", 
            variable=dupevar, onvalue=True)

# buttons for recording this map, recording exceptions, and removing selected records
add1_btn = ttk.Button(options, text='Record this map', command=record_this_map, state=tk.DISABLED)
exception_btn = ttk.Button(options, text='Record an exception', command=lambda: record_exception(grab_dd_values()), state=tk.DISABLED)
remove_btn = ttk.Button(options, text='Remove selected record', command=remove_selected_record, state=tk.DISABLED)

# set up a space on the main window for dialog messages to be displayed to the user
dialogContents = tk.StringVar()
dialog = ttk.Label(options)
dialog['textvariable'] = dialogContents

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
header.grid(row=0, column=0, columnspan=7, rowspan=1, pady=5)
title.grid(row=0, column=0, columnspan=5, rowspan=1, padx=100, pady=5)
sign_in_label.grid(row=0, column=5)
initials.grid(row=0, column=6, padx=20)

# ---- options frame ----
options.grid(row=1, column=0, columnspan=7, rowspan=8, pady=5)

for idx, dd in enumerate(dropdowns):
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
dialog.grid(row=8, column=3, columnspan=3, rowspan=1, pady=5, sticky='s') # dialog label

# ---- table frame ----
table.grid(row=9, column=0, columnspan=7, rowspan=1, pady=5)
tbl.grid(row=9, column=0, columnspan=6, rowspan=1) # table 
tbl_scroll.grid(row=9, column=6, rowspan=1, sticky='ns') # table scroll bar

# ------------------------------ RUN THE TOOL ----------------------------------
root.mainloop()