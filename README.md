# geodata_map_inventory
GUI and SQLite backed for inventorying USGS maps

Completed:
- reading in the USGS topo data into a nested dictionary structure
- basic skeleton of the GUI window
- drop-down selections narrowing down the possible options for other dropdowns
- autofilling drop-downs for which there is only one possible value
- functional prev/next buttons for incrementing drop-downs without having to click into them first
- basic interactions (read and write) with SQLite database file on the shared drive, triggered by buttons
- connected insert to the table display, and got remove selected to be functional
- the insert and remove methods confirm that the remote database was changed appropriately before proceeding
- debugged the issue that prevented button-binding in a for loop
- added a "sign-in" drop down for users to select initials on each runtime based on a local csv
- worked around floats issue by reading everything as strings and sorting by key
- changed "we have multiple" to just a duplicate checkbox (not necessary to store quantities)
- added a section of the GUI for displaying messages of success or error
- updated database to include recorded_by, recorded_time, is_damaged, and is_duplicate columns
- signing in updates table display with 10 most recently recorded maps
- remove method checks for number of items selected and prints messages if it's anything other than 1
- a confirmation window pops up to confirm removal before executing it
- functionality for multiple matching records (pop-up window with links and radiobutton)
- exception handling table is created, methods for reading GNIS's and generating unique IDs are complete, state/quad selections are bound
- exception handling window is created, insert exception method is complete, and sign-in method is updated to accommodate both tables
- pre-loading of exception information from main window is complete, and remove selected method is updated
- both tables have a producer column, and most recent 10 methods are updated to reflect that

To-do:
- verify that for duplicate gnis IDs its safe to just choose the Standard one - do we have over or undersized maps
- should exception IDs be uniquely identifiable by map attributes?
- should the pre-loading carry over stuff that's locked in? it currently does
- should the pre-loading disable whatever is pre-loaded from being manipulated?
- generate new id should maybe have a list of available IDs that can also be replenished upon removals
- comment and reorganize code (next: read_topos should take columns as an ordered input parameter)

columns in exceptions table:db everything in exception window (normal map stuff plus series sheet edition), id, recorded by, recorded time
on the exceptions window, the fab five will be text entry, but map scale, state, and cell name will also be drop-downs
state and cell will be hooked up to each other, but not map scale.  this might require a new read-in method, with GNIS as the value
map year and print year will just be text entry, restricted to 4-character numerical values
I don't know if entry should be restricted to 1 menu at a time, or just open-season (will do latter for now)
producer will be a radiobutton (maybe with an Other text entry, maybe not)
we will still have checkboxes for duplicate and damage, and then a record this map
sign-in methods will need to adjusted to get top ten from either of the tables, not just the one
remove selected record will also need a way of navigating multiple tables depending on what is selected

Important notes:
- writing to the network db file does not work when someone has the db in writing
mode in SQLite.  Python will throw an error saying the database is locked. We can
have the db open in DB Browser manually while the script runs, but only in reading mode. 
If we need to make manual changes in DB Browser, make them, but be sure to hit 
"Write Changes" (Ctrl-S) to get out of writing mode before running the script again. 
