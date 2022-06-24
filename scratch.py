from tkinter import *
from tkinter import ttk
from tkinter.ttk import Treeview
import sqlite3
import file_io

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS routers (id INTEGER PRIMARY KEY, hostname text, brand text, ram integer, flash integer)")
        self.conn.commit()

    def fetch(self, hostname=''):
        self.cur.execute(
            "SELECT * FROM routers WHERE hostname LIKE ?", ('%'+hostname+'%',))
        rows = self.cur.fetchall()
        return rows

    def fetch2(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        return rows

    def insert(self, hostname, brand, ram, flash):
        self.cur.execute("INSERT INTO routers VALUES (NULL, ?, ?, ?, ?)",
                         (hostname, brand, ram, flash))
        self.conn.commit()

    def remove(self, id):
        self.cur.execute("DELETE FROM routers WHERE id=?", (id,))
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