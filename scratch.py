import sqlite3
import file_io

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def fetch(self, scan_id):
        self.cur.execute(
            "SELECT * FROM all_usgs_topos WHERE scan_id = " + str(scan_id))
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

# import urllib.request
# import io
# from PIL import Image, ImageTk
# root = Tk()
# images = []
# fake_csv = [[1, "blue", 4, "pillow"], [2, "red", 12, "horse"]]
# mapthumb = 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/HistoricalTopo/PDF/AK/25000/AK_Anchorage%20B-7%20NW_353597_1979_25000_tn.jpg'

# for i in range(0, 1): # changed from 8 to 1 from https://stackoverflow.com/questions/38173526/displaying-images-from-url-in-tkinter
#     raw_data = urllib.request.urlopen(mapthumb).read()
#     im = Image.open(io.BytesIO(raw_data))
#     image = ImageTk.PhotoImage(im)
#     label1 = Label(root, image=image)
#     label1.grid(row=i, sticky=W)

#     # append to list in order to keep the reference
#     images.append(image)
# root.mainloop()

if __name__ == "__main__":
    tdb = Database('//files.brown.edu/DFS/Library_Shared/_geodata/maps/maps_we_have_test.db')
    print(tdb.fetch(362330))