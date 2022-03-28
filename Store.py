# Class for managing sqlite3 database
import sqlite3

DATABASE = "listings.sqlite"

class Store:
    """
    Class for managing database handling listings.
    """
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.last_key = None

    def add_listing(self, ID, title, price, end_timestamp, image, notified):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO LISTING (ID, TITLE, PRICE, END_TIMESTAMP, IMAGE, NOTIFIED) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (ID, title, price, end_timestamp, image, notified))
            connection.commit()
            self.last_key = cursor.lastrowid

    def delete_listing(self, ID):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            connection.commit()
    
    def update_listing(self, ID, title, price, end_timestamp, image, notified):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE LISTING SET TITLE = ?, PRICE = ?, END_TIMESTAMP = ?, IMAGE = ?, NOTIFIED = ? WHERE (ID = ?)"
            cursor.execute(query, (title, price, end_timestamp, image, notified, ID))
            connection.commit()

    def set_listing_notified(self, ID):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "UPDATE LISTING SET NOTIFIED = TRUE WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            connection.commit()

    def get_listing(self, ID):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT ID, TITLE, PRICE, END_TIMESTAMP, IMAGE, NOTIFIED FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            return_tuple = tuple(cursor.fetchone())
        return return_tuple

    def get_listings(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT ID, TITLE, PRICE, END_TIMESTAMP, IMAGE, NOTIFIED FROM LISTING ORDER BY ID"
            cursor.execute(query)
            listings = [(ID, (title, price, end_timestamp, image, notified))
                      for ID, title, price, end_timestamp, image, notified in cursor]
        return listings