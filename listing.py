from typing import Union


class Listing:
    def __init__(
        self,
        ID: Union[int, str],
        title: str,
        price: Union[float, str],
        end_timestamp: Union[int, str],
        image_url: str,
        notified: Union[bool, str],
    ) -> None:
        self.ID = int(ID)
        self.title = title
        self.price = float(price)
        self.end_timestamp = int(end_timestamp)
        self.image_url = image_url
        self.notified = bool(notified)

    def __getitem__(self, index):
        if index == 0:
            return self.ID
        elif index == 1:
            return self.title
        elif index == 2:
            return self.price
        elif index == 3:
            return self.end_timestamp
        elif index == 4:
            return self.image_url
        elif index == 5:
            return self.notified
        else:
            # If index is outside of these options then:
            raise IndexError

    def __repr__(self) -> str:
        # Iterates over self and returns it in a tuple format
        return "Listing: " + str(tuple(self))


def testListing():
    listing = Listing(12321, "Test Listing", 120.1, 1648933576, "test url", False)
    print(listing)


if __name__ == "__main__":
    testListing()
