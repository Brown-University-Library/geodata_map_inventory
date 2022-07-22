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
- added a "sign-in" drop down for users to enter initials on each runtime, which are saved locally
- worked around floats issue by reading everything as strings and sorting by key
- changed "we have multiple" to just a duplicate checkbox (not necessary to store quantities)
- added a section of the GUI for displaying messages of success or error
- updated database to include recorded_by, recorded_time, is_damaged, and is_duplicate columns
- signing in updates table display with 10 most recently recorded maps
- remove method checks for number of items selected and prints messages if it's anything other than 1
- a confirmation window pops up to confirm removal before executing it
- functionality for multiple matching records (pop-up window with links and radiobutton)

To-do:
- the checkboxes for damage and duplicate are reset to false after each map is recorded
- aesthetics / config stuff for removal confirmation window or multiple matches window?
- implement exception handling (new table)
- label and comment code more

Important notes:
- writing to the network db file does not work when someone has the db in writing
mode in SQLite.  Python will throw an error saying the database is locked. We can
have the db open in DB Browser manually while the script runs, but only in reading mode. 
If we need to make manual changes in DB Browser, make them, but be sure to hit 
"Write Changes" (Ctrl-S) to get out of writing mode before running the script again. 