# Class for managing sqlite3 database
import sqlite3

class Store:
    """
    Class for managing the listings database
    """
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.last_key = None
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "CREATE TABLE IF NOT EXISTS LISTING (ID INTEGER PRIMARY KEY, TITLE TEXT, PRICE INTEGER, END_TIMESTAMP INTEGER, IMAGE TEXT, NOTIFIED BOOL)"
            cursor.execute(query)
            connection.commit()
        pass

    def add_listing(self, ID, title, price, end_timestamp, image, notified):
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()

            # Check to see if listing ID already exists
            query = "SELECT ID, TITLE, PRICE, END_TIMESTAMP, IMAGE, NOTIFIED FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            if not cursor.fetchone() == None:
                connection.commit()
                return False
            
            # If it doesn't then insert it
            query = "INSERT INTO LISTING (ID, TITLE, PRICE, END_TIMESTAMP, IMAGE, NOTIFIED) VALUES (?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (ID, title, price, end_timestamp, image, notified))
            connection.commit()
            self.last_key = cursor.lastrowid
            return True

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

def db_test():
    print("Testing Database")
    print("Making Store object...")
    my_store = Store("test.sqlite")
    print("Creating Table")
    my_store.create_table()
    print("Adding Test Listing [102, 'Test Title 2', 421, 1648438552, 'https://testimage.url', False]")
    result = my_store.add_listing(103, 'Test Title 3', 1000000, 1648438552, 'https://testimage.url', True)
    if result:
        print("Added row")
    else:
        print("Failed to add row")
    print("Retrieving all listings:")
    print(my_store.get_listings())
    pass

if __name__ == "__main__":
    db_test()