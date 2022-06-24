# Ethan McIntosh - GIS and Data Services - Brown University Library - summer 2022
# 
# Methods for reading files in and out of Python data structures for map
# inventory project.

import pandas as pd

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

    # read csv into df
    topo_df = pd.read_csv(filepath, usecols=columns).fillna("")
    topos = topo_df.values.tolist()

    for topo in topos:
        # unpack values of list into variables
        id, quad, state, scale, map_year, print_year, url = topo

        # initialize dictionary structure as needed
        if scale not in maps:
            maps[scale] = {}
        if state not in maps[scale]:
            maps[scale][state] = {}
        if quad not in maps[scale][state]:
            maps[scale][state][quad] = {}
        if map_year not in maps[scale][state][quad]:
            maps[scale][state][quad][map_year] = {}
        if print_year not in maps[scale][state][quad][map_year]:
            maps[scale][state][quad][map_year][print_year] = []
        
        # populate values for each row
        maps[scale][state][quad][map_year][print_year].append((id, url))

# other methods that might belong here include reading / writing user sessions,
# and maybe even the SQLite database calls.

if __name__ == '__main__':
    # example of how to call read_topos()
    mymaps = {}
    read_topos('usgs_topos.csv', mymaps)
    print(mymaps[24000]['Oregon']['Sparta'][1988])

