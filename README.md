# geodata_map_inventory
GUI and SQLite backed for inventorying USGS maps

Completed:
- reading in the USGS topo data into a nested dictionary structure
- basic skeleton of the GUI window
- drop-down selections narrowing down the possible options for other dropdowns
- autofilling drop-downs for which there is only one possible value
- basic prev/next functionality for incrementing drop-downs without having to click into them first
- basic interactions (read and write) with SQLite database file on the shared drive, triggered by buttons

To-do:
- add prev/next options for the drop-downs (all? some?)
- consider pointing to the different parts of the nested dictionary within the labeled
drop down menu object, or just somehow rework the traverse / working dict / get values stuff
- add a section of the GUI for displaying messages that doesn't require acknowledgement
- finish the methods for table display and remove selected record
- label and comment code more
- figure out how to handle floats for print year programmatically (not high priority)

Important notes:
- writing to the network db file does not work when someone is actively editing it in SQLite - 
the script will throw an error saying the database is locked. The script can write to
the db while I have it open manually as long as I'm not manually in writing mode.