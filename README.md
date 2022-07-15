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


To-do:
- add a section of the GUI for displaying messages, ideally that would fade out after a short time
- change "we have multiple" to just a duplicate checkbox (not necessary to store quantities)
- update sign-in to display most recent table (last ten records from the given user)
- to do that, the user would need to be a record-level attribute, and we'd also need a dropdown/textbox asking for initials
- modify insert method to check whether the database already has a record with that scan id.  
- implement damage handling (new table or new column?)
- implement we have 1 when there are multiple (new pop-up with links, dmg boxes, mutually exclusive selection, disabled quantity boxes)
- implement exception handling (new table)
- label and comment code more

Important notes:
- writing to the network db file does not work when someone has the db in writing
mode in SQLite.  Python will throw an error saying the database is locked. We can
have the db open in DB Browser manually while the script runs, but only in reading mode. 
If we need to make manual changes in DB Browser, make them, but be sure to hit 
"Write Changes" (Ctrl-S) to get out of writing mode before running the script again. 