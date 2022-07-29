# Ethan McIntosh - GIS and Data Services - Brown University Library - summer 2022
# 
# Methods for reading files in and out of Python data structures for map
# inventory project.

import pandas as pd
import csv

def read_next_exception_id(filepath):
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            return row[0]

def write_next_exception_id(filepath, next_exc_id):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow([next_exc_id])

def read_users(filepath:str, users: list):
    """reads a csv file with a single column listing users, appends them to a list"""
    with open(filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            users.append(row[0])
    return users

def write_users(filepath:str, users):
    """given an iterable set of users, writes a csv file listing them in 1 column"""
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\n')
        writer.writerow(list(users))

def read_gnis(filepath:str, cells:dict):
    # these are the column names corresponding to the lookup parameters
    columns = ['gnis_cell_id', 'cell_name', 'primary_state', 'cell_type', 'map_scale']
    # read csv into df, selecting specified columns
    topo_df = pd.read_csv(filepath, usecols=columns, dtype=str).drop_duplicates()
    topo_df = topo_df[[x.startswith('Standard') for x in topo_df.cell_type]]
    # topo_df['print_year'] = topo_df['print_year'].astype('Int64')
    topos = topo_df.values.tolist()

    for topo in topos:
        # unpack values of list into variables
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
    print year 1999, calling maps[24000]['Oregon']['Salem'][1988][1999] would 
    yield a list of tuples with the (scan ID, product URL) of each matching map.
    """
    # these are the column names corresponding to the lookup parameters
    columns = ['scan_id', 'cell_name', 'primary_state', 'map_scale', 
                'date_on_map', 'print_year', 'product_url']

    # read csv into df, selecting specified columns
    topo_df = pd.read_csv(filepath, usecols=columns, dtype=str).fillna("(none)")
    # topo_df['print_year'] = topo_df['print_year'].astype('Int64')
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

# other methods that might belong here include reading / writing user sessions,
# and maybe even the SQLite database calls.

if __name__ == '__main__':
    # examples of how to call read_topos() and read_gnis()
    mymaps = {}
    read_topos('usgs_topos.csv', mymaps)
    print(mymaps['24000']['Oregon']['Sparta'])
    # print("{:2f}".format(1971))
    mycells = {}
    read_gnis('usgs_topos.csv', mycells)
    print(mycells['Oregon']['Sparta'])

