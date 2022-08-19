# Welcome to the BUL Topo Map Inventory Tool
This is a Python command-line tool that we built to help us take inventory of the topographic maps in Brown University's map collection in the Sciences Library. Instead of having people manually record the attributes of each map, we set up a graphical user interface with tkinter which allows people to select the key attributes of each map using drop-down menus and buttons. The options available in each drop-down menu are populated with data from the USGS Historical Topographic Map Collection (HTMC), and the menus are dynamically updated based on user selections, allowing users to match each physical map to its corresponding digital record with as little hassle as possible. Checkboxes allow users to flag maps that are damaged or for which we have duplicates, and there is a workflow for recording "exception" maps, or topographic maps that are filed in our collection but aren't part of the HTMC, even if they use some of the same attribute schema. Behind the scenes, information about each map that we record using the tool is stored in a SQLite database.

### Requirements for running the tool
- You need to be granted access to the Brown University Library shared drive.
- Your computer needs to have Python 3 or higher installed.
- You need to install the pandas module into your Python interpreter, if you don't have it already. All other modules needed for the tool are in the Python Standard Library.

### How to run the tool
1. Clone this repository somewhere on your computer.
2. Open a terminal with the geodata_map_inventory folder as the working directory.
3. Run either ```python bul_topo_tool.py``` or ```python3 bul_topo_tool.py```, depending on how your Python is set up.
4. The tool should open in its own window. To stop the program, just close the window.

### File Descriptions
| file name | description                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| bul_topo_tool.py | This is the only .py file that's meant to be run directly. Everything else is "supporting material". Any code having to do with the graphics and layout of the tool is here, and so is most of the logic governing what different buttons do and how they interact with each other. |
| file_io.py | These methods are for getting data in and out (io) of the csv files in this repository.
| db.py | These methods are for using SQL commands to interact with the .db file on the library shared drive where our topo map inventory data gets stored.
| usgs_topos.csv | A table with information about every map in the USGS's [Historical Topographic Map Collection](https://www.usgs.gov/programs/national-geospatial-program/historical-topographic-maps-preserving-past) (HTMC). |
| users.csv | A list of authorized users of the BUL Topo Map Inventory Tool (initials only). |
| next_exception_id.csv | Stores a 5-digit number that will be assigned as the unique identifier of the next "exception map" we find (any map that's physically in our collection but isn't part of the HTMC. Each time we record an exception map, this number gets updated.)

### Development Notes

This is a tkinter application built around 2 custom data structures: an AutocompleteCombobox (a drop-down menu that autocompletes typed-in entries) and a LabeledDropDownMenu, which bundles together a drop-down menu with other tkinter widgets and links these bundled objects to each other in a hierarchical order, which facilitates the dynamic updating of one menu's options based on user selections on the others. 

The main executable script file (bul_topo_tool.py) is organized into sections, starting with the code for these custom classes. Below that are sections for tool initialization, recording regular maps, recording exception maps, removing records, and miscellaneous operations, all of which solely consist of methods. The code that actually builds the main tool window and runs the application is at the bottom, after the methods.

### Scratch

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
- all drop-downs on the main window now have autocomplete

Important notes:
- writing to the network db file does not work when someone has the db in writing
mode in SQLite.  Python will throw an error saying the database is locked. We can
have the db open in DB Browser manually while the script runs, but only in reading mode. 
If we need to make manual changes in DB Browser, make them, but be sure to hit 
"Write Changes" (Ctrl-S) to get out of writing mode before running the script again. 
