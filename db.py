# Ethan McIntosh - GIS and Data Services - Brown University - summer 2022
#
# This is where the SQLite database class definition and methods will live

import sqlite3

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def fetch(self, scan_id):
        self.cur.execute(
            "SELECT * FROM usgs_topos_we_have WHERE scan_id = " + str(scan_id))
        rows = self.cur.fetchall()
        return rows

    # worth noting that execute() does have a two-argument mode where the first arg is a wild-carded SQL
    # and the second arg is a tuple listing variables or values you want to sub in for those wild cards. Example:
    # self.cur.execute("UPDATE routers SET hostname = ?, brand = ? WHERE id = ?", (hostname, brand, id))

    def insert(self, scan_id):
        self.cur.execute("INSERT INTO usgs_topos_we_have SELECT * FROM all_usgs_topos WHERE scan_id = " + str(scan_id))
        self.conn.commit()

    def remove(self, scan_id):
        self.cur.execute("DELETE FROM usgs_topos_we_have WHERE scan_id = " + str(scan_id))
        self.conn.commit()

    def update(self, id, hostname, brand, ram, flash):
        self.cur.execute("UPDATE routers SET hostname = ?, brand = ?, ram = ?, flash = ? WHERE id = ?",
                         (hostname, brand, ram, flash, id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    tdb = Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/maps_we_have_test.db')
    print(tdb.fetch(362330))