# Ethan McIntosh - GIS and Data Services - Brown University Library - August 2022

import pandas as pd
import csv

def read_next_exception_id(filepath):
    """Reads and returns the value in the first row and first column of a given
    csv file, representing the next available map ID for exception maps.
    
    filepath: a csv file storing the next available exception map ID in its first 
    row and first column"""
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            return row[0]

def write_next_exception_id(filepath, next_exc_id):
    """Writes a given next exception map ID into the first row and first column
    of a given csv file, replacing what was there before.
    
    next_exc_id: the next available exception map ID
    filepath: a csv file storing the next available exception map ID in its first 
    row and first column"""
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow([next_exc_id])

def read_users(filepath:str):
    """reads a csv file with a single column listing map inventory application 
    users and returns the values as a list
    
    filepath: a csv file storing a list of possible users in its first column"""
    users = []
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            users.append(row[0])
    return users

def read_gnis(filepath:str, cells:dict):
    """Reads tabular-format data on topographic maps from the csv table of all USGS
    topographic maps that were ever made into a nested dictionary structure, 
    such that records can be accessed using dictionary calls.  For a 1:24000 map
    of Salem, Oregon, calling cells['Oregon']['Salem'] yields a list of tuples 
    with the (map scale, GNIS cell ID) of each matching map.  Organizing the
    information in this way makes it quick to filter cell names based on selections
    of primary states, and quick to look up matching GNIS cell IDs for recording
    exception maps.
    
    filepath: csv table of all USGS topographic maps that were ever made
    cells: a (usually empty) dict in which to populate the nested dictionary structure"""

    # these are the column names corresponding to the lookup parameters
    columns = ['gnis_cell_id', 'cell_name', 'primary_state', 'cell_type', 'map_scale']

    # read csv into df, selecting specified columns, stringifying everything, dropping duplicates
    topo_df = pd.read_csv(filepath, usecols=columns, dtype=str).drop_duplicates()

    # only consider standard maps - not oversized or undersized maps.  This step
    # makes it so that GNIS cell IDs are unique to each scale / state / cell name combination
    topo_df = topo_df[[x.startswith('Standard') for x in topo_df.cell_type]]
    
    # some territories have no standard maps, but need them to appear in
    # exceptions dropdown menu
    ttory=pd.DataFrame(
        [['','','American Samoa','','24000'],
          ['','','Guam','','24000'],
          ['','','Federated States of Micronesia','','25000'],
          ['','','Northern Mariana Islands','','25000'],
          ['','','Republic of Palau','','25000']],
          index=[1,2,3,4,5],
          columns=columns)
    topo_df=pd.concat([topo_df,ttory])
    
    topos = topo_df.values.tolist()
    for topo in topos:
        # unpack values of each row (i.e. each map) into named variables
        gnis, quad, state, cell_type, scale = topo

        # initialize nested dictionary structure as needed
        if state not in cells:
            cells[state] = {}
        if quad not in cells[state]:
            cells[state][quad] = []
        
        # populate values for each row
        cells[state][quad].append((scale, gnis))

def read_topos(filepath:str, maps:dict):
    """
    Reads tabular-format data on topographic maps from the csv table of all USGS
    topographic maps that were ever made into a nested dictionary structure, 
    such that map records are hierarchically organized by map scale, primary 
    state, quad name, map year, and print year, in that order.  Populates the 
    dictionary that is passed in (maps) such that records can be accessed using 
    dictionary calls.  For a 1988 map at 1:24000 scale of Salem, Oregon with 
    print year 1999, calling maps[24000]['Oregon']['Salem'][1988][1999] yields 
    a list of tuples with the (scan ID, product URL) of each matching map.  This
    structure of data is useful for quickly filtering down the database of maps 
    upon each mouse selection of attributes, and also facilitates fast lookup of
    scan IDs and product URLs when recording USGS topo maps.
    
    filepath: csv table of all USGS topographic maps that were ever made
    maps: a (usually empty) dict in which to populate the nested dictionary structure"""
    # these are the column names corresponding to the lookup parameters
    columns = ['scan_id', 'cell_name', 'primary_state', 'map_scale', 
                'date_on_map', 'print_year', 'product_url']

    # read csv into df, selecting specified columns and stringifying everything
    # also fills in any missing values with the string "(none)" so that dropdown
    # menus for the data have a (none) option instead of just a blank option
    # option instead of just a blank option
    topo_df = pd.read_csv(filepath, usecols=columns, dtype=str).fillna("(none)")

    topos = topo_df.values.tolist()
    for topo in topos:
        # unpack values of list into variables
        id, quad, state, scale, map_year, print_year, url = topo

        # initialize nested dictionary structure as needed
        if scale not in maps:
            maps[scale] = {}
        if state not in maps[scale]:
            maps[scale][state] = {}
        if quad not in maps[scale][state]:
            maps[scale][state][quad] = {}
        if map_year not in maps[scale][state][quad]:
            maps[scale][state][quad][map_year] = {}
        if print_year not in maps[scale][state][quad][map_year]:
            # initialize empty list for the (id, url) of each matching map
            maps[scale][state][quad][map_year][print_year] = []
        
        # populate values for each row
        maps[scale][state][quad][map_year][print_year].append((id, url))