# Ethan McIntosh - GIS and Data Services - Brown University - summer 2022
#
# This is where the SQLite database class definition and methods will live

import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def fetch(self, table, id_name, id_val):
        query = "SELECT * FROM {} WHERE {} = ?".format(table, id_name)
        self.cur.execute(query, (id_val,))
        rows = self.cur.fetchall()
        return rows
    
    def fetch_most_recent(self, initials):
        self.cur.execute(
            "SELECT scan_id, map_scale, primary_state, cell_name, date_on_map, print_year, is_damaged, is_duplicate " + 
            "FROM usgs_topos_we_have WHERE recorded_by = ? ORDER BY recorded_time DESC LIMIT 10", (initials,))
        rows = self.cur.fetchall()
        return rows

    def insert_topo(self, scan_id, recorded_by, recorded_time, is_damaged, is_duplicate):
        self.cur.execute("INSERT INTO usgs_topos_we_have SELECT *, ?, ?, ?, ? FROM all_usgs_topos WHERE scan_id = ?", (recorded_by, recorded_time, is_damaged, is_duplicate, scan_id))
        self.conn.commit()

    def remove(self, table, id_name, id_val):
        query = "DELETE FROM {} WHERE {} = ?".format(table, id_name)
        self.cur.execute("DELETE FROM usgs_topos_we_have WHERE scan_id = ?", (id_val,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    tdb = Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/maps_we_have_test.db')
    print(tdb.fetch(362330))