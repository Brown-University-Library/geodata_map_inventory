# geodata_map_inventory
GUI and SQLite backed for inventorying USGS maps

Completed:
- reading in the USGS topo data into a nested dictionary structure
- basic skeleton of the GUI window
- drop-down selections narrowing down the possible options for other dropdowns
- debugged the issue that prevented button-binding in a for loop
- autofilling drop-downs for which there is only one possible value
- basic prev/next functionality for incrementing drop-downs without having to click into them first
- basic interactions (read and write) with SQLite database file on the shared drive, triggered by buttons

To-do:
- add prev/next options for the drop-downs (all? some?)
- consider pointing to the different parts of the nested dictionary within the labeled
drop down menu object, or just somehow rework the traverse / working dict / get values stuff
- add a section of the GUI for displaying messages that doesn't require acknowledgement
- finish the methods for table display and remove selected record
- initial table display should show maybe the last ten records from the given user
- to do that, the user would need to be a record-level attribute, and we'd also need a dropdown/textbox asking for initials
- modify insert method to check whether the database already has a record with that scan id.  
- implement damage handling (new table or new column?)
- implement we have 1 when there are multiple (new pop-up with links, dmg boxes, mutually exclusive selection, disabled quantity boxes)
- implement we have multiple (if 1 record, just enter quantity, else the links popup but with multiple selection and type-in qty boxes)
- implement exception handling (new table)
- label and comment code more
- figure out how to handle floats for print year programmatically (not high priority)

Important notes:
- writing to the network db file does not work when someone is actively editing it in SQLite - 
the script will throw an error saying the database is locked. The script can write to
the db while I have it open manually as long as I'm not manually in writing mode.