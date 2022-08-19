# Ethan McIntosh - GIS and Data Services - Brown University - August 2022

import sqlite3

class Database:
    def __init__(self, db):
        """initializing a Database object sets up a connection and a cursor for
        querying a given .db file"""
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def fetch(self, table, id_name, id_val):
        """Queries a given table for all records for a given id_name
        matching a given id_val, and returns a list of matching records."""
        query = "SELECT * FROM {} WHERE {} = ?".format(table, id_name)
        self.cur.execute(query, (id_val,))
        rows = self.cur.fetchall()
        return rows
    
    def fetch_most_recent(self, table, id_name, user):
        """Method for returning table display information (column names are hard-coded) for up to 10 of the most recent
        maps in a given table with a given ID name that were recorded by a given user.
        """
        cols = "producer, map_scale, primary_state, cell_name, date_on_map, print_year, is_damaged, is_duplicate, recorded_time"
        query = "SELECT {}, {} FROM {} WHERE recorded_by = ? ORDER BY recorded_time DESC LIMIT 10".format(id_name, cols, table)
        self.cur.execute(query, (user,))
        rows = self.cur.fetchall()
        return rows

    def insert_topo(self, scan_id, recorded_by, recorded_time, is_damaged, is_duplicate, producer):
        """Inserts a record for a USGS topo map by copying over the information about that map from the all topos table.
        Assumes the existence of both an all_usgs_topos table containing a scan_id and a usgs_topos_we_have table
        containing all of the fields of all_usgs_topos plus five extra, whose values for a given map are passed in"""
        self.cur.execute("INSERT INTO usgs_topos_we_have SELECT *, ?, ?, ?, ?, ? FROM all_usgs_topos WHERE scan_id = ?"
                        , (recorded_by, recorded_time, is_damaged, is_duplicate, producer, scan_id))
        self.conn.commit()

    def insert_exception(self, exception_vals):
        """Given a ordered set of 15 values for a given exception map, inserts those values into the exception_maps_we_have table"""
        cols = "(map_id, producer, map_scale, primary_state, cell_name, gnis_cell_id, "+\
            "date_on_map, print_year, sheet, series, edition, is_damaged, is_duplicate, recorded_by, recorded_time)"
        self.cur.execute("INSERT INTO exception_maps_we_have " + cols + " VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                        , exception_vals)
        self.conn.commit()

    def remove(self, table, id_name, id_val):
        """Deletes records from a given table with a given ID name matching a given ID value"""
        query = "DELETE FROM {} WHERE {} = ?".format(table, id_name)
        self.cur.execute(query, (id_val,))
        self.conn.commit()

    def __del__(self):
        """Close the connection to the db file when the Database object stops running"""
        self.conn.close()