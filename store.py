# Class for managing sqlite3 database
import sqlite3
from listing import Listing
from typing import List, Union


class Store:
    """
    Class for managing the listings database
    """

    NON_KEYS = "TITLE, PRICE, END_TIMESTAMP, IMAGE_URL, NOTIFIED"

    def __init__(self, dbfile: str) -> None:
        self.dbfile = dbfile
        self.last_key = None
        self.create_table()

    def create_table(self) -> None:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = (
                "CREATE TABLE IF NOT EXISTS LISTING"
                "(ID INTEGER PRIMARY KEY,"
                " TITLE TEXT,"
                " PRICE INTEGER,"
                " END_TIMESTAMP INTEGER,"
                " IMAGE_URL TEXT,"
                " NOTIFIED BOOL)"
            )
            cursor.execute(query)
            connection.commit()

    def add_listing(self, listing: Listing) -> bool:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()

            # Check to see if listing ID already exists
            query = f"SELECT ID, {self.NON_KEYS} FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (listing.ID,))
            if not cursor.fetchone() == None:
                connection.commit()
                return False

            # If it doesn't then insert it
            query = (
                f"INSERT INTO LISTING (ID, {self.NON_KEYS}) VALUES (?, ?, ?, ?, ?, ?)"
            )
            cursor.execute(query, (*listing,))
            connection.commit()
            self.last_key = cursor.lastrowid
            return True

    def delete_listing(self, ID: Union[int, str]) -> None:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "DELETE FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            connection.commit()

    def update_listing(self, listing: Listing) -> None:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = (
                "UPDATE LISTING SET TITLE = ?, PRICE = ?, END_TIMESTAMP = ?,"
                " IMAGE_URL = ?, NOTIFIED = ? WHERE (ID = ?)"
            )
            (_, *non_keys) = listing  # Tuple unpacking to exclude first (ID)
            cursor.execute(query, (*non_keys, listing.ID))
            connection.commit()

    def get_listing(self, ID: Union[int, str]) -> Listing:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = f"SELECT ID, {self.NON_KEYS} FROM LISTING WHERE (ID = ?)"
            cursor.execute(query, (ID,))
            result = cursor.fetchone()
            if result is None:
                raise KeyError("No listing with the ID exists")
            listing = Listing(*result)
        return listing

    def get_listings(self) -> List[Listing]:
        with sqlite3.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = f"SELECT ID, {self.NON_KEYS} FROM LISTING ORDER BY ID"
            cursor.execute(query)
            listings = [
                Listing(ID, title, price, end_timestamp, image_url, notified)
                for ID, title, price, end_timestamp, image_url, notified in cursor
            ]
        return listings


def db_test() -> None:
    print("Testing Database")
    print("Making Store object...")
    my_store = Store("test.sqlite")

    print("Creating Table")
    my_store.create_table()

    test_listing = Listing(
        104, "Test Title 4", 1337, 13123123, "https://testimage.url", True
    )
    print("Adding Test Listing: {test_listing}")

    # Update listing
    # my_store.update_listing(test_listing)
    # Add Listing
    # if my_store.add_listing(test_listing):
    #     print("Added row")
    # else:
    #     print("Failed to add row")
    print("Retrieving all listings:")
    print(my_store.get_listings())


if __name__ == "__main__":
    db_test()
