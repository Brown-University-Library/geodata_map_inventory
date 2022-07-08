# geodata_map_inventory
GUI and SQLite backed for inventorying USGS maps

Completed:
- reading in the USGS topo data into a nested dictionary structure
- basic skeleton of the GUI window
- drop-down selections narrowing down the possible options for other dropdowns
- autofilling drop-downs for which there is only one possible value
- basic prev/next functionality for incrementing drop-downs without having to click into them first
- basic interactions (read and write) with SQLite database file on the shared drive

To-do:
- add prev/next options for the drop-downs (all? some?)
- fill out "we have 1" logic - check for multiples
- label and comment code more
- figure out how to handle floats for print year programmatically (not high priority)

Important notes:
- writing to the network db file does not work when someone has it manually open in SQLite - 
the script will throw an error saying the database is locked