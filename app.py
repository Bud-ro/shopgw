from flask import Flask
import apprise
from os import environ
from store import Store
import requests
import bs4
from listing import Listing
import re
import time

# Global variables
current_listing_ID = 141163191  # Can set to approximate start or or None
# Gets overwritten if .config file exists
# .config uses JSON to store users email and filter lists
filter_list = ["record", "vinyl", "LP", "cassette", "beta", "laser disk"]

# Load .env
DISCORD_WEBHOOK_LINK = environ.get("DISCORD_WEBHOOK_LINK")
DATABASE = "listings.sqlite"  # Located in local directory
db = Store(DATABASE)

app = Flask(__name__)
apobj = apprise.Apprise()
apobj.add(DISCORD_WEBHOOK_LINK)


@app.route("/")
def index() -> str:
    return f"Apprise link: {DISCORD_WEBHOOK_LINK}"


@app.route("/db/")
def db_test() -> str:
    return str(db.get_listings())


# @app.route("/getfirst/<int:start_index>")
def find_first_listing(start_index: int) -> int:
    """
    Initializes our app by finding the oldest listing that is still active.
    Returns the ID of the approximate first active listing. This method is innaccurate
    since listings have different times they are active for.
    """
    app.logger.info("Finding first listing")
    ID = start_index
    now = int(time.time())  # UNIX time at the beginning of the call
    high = 0
    low = 0

    # First find upper bound
    while True:
        status = fetch_listing(ID)
        listing = db.get_listing(ID)  # Assume listing exists and is expired
        if listing.end_timestamp < now:
            low = ID
            ID += 20000  # There are about 20000 per day
        else:
            high = ID
            break

    # Binary search time
    while low <= high:
        ID = (high + low) // 2
        fetch_listing(ID)
        listing = db.get_listing(ID)
        if listing.end_timestamp < now:
            low = ID + 1
        elif listing.end_timestamp > now:
            high = ID - 1

        app.logger.info(f"Low: {low}, ID: {ID}, High: {high}")
        time.sleep(2)
    return ID


@app.route("/listing/<int:ID>")
def display_listing(ID: int) -> str:
    try:
        listing = db.get_listing(ID)
    except KeyError:
        status = fetch_listing(ID)
        if status:
            listing = db.get_listing(ID)
        else:
            listing = "Listing does not exist"
    return str(listing)


def time_from_now(time_str: str) -> int:
    """Returns UNIX time in the future based on time_str"""
    """-1 signifies that the auction has already ended"""
    current_time = int(time.time())
    time_to_end = 0
    if time_str == "Auction Ended":
        return -1
    for duration in time_str.split(" "):
        if "d" in duration:
            time_to_end += int(duration[:-1]) * 86400
        elif "h" in duration:
            time_to_end += int(duration[:-1]) * 3600
        elif "m" in duration:
            time_to_end += int(duration[:-1]) * 60
        elif "s" in duration:
            time_to_end += int(duration[:-1])
    future_timestamp = current_time + time_to_end
    return future_timestamp


# @app.route("/rawlisting/<int:ID>")
def fetch_listing(ID: int) -> bool:
    """
    Requests https://shopgoodwill.com/item/{ID} and scrapes for information using bs4
    Returns true if listing exists, for 404's returns False
    """

    headers = {"User-Agent": "Mozilla/5.0"}
    # Doesn't fully load the page, however all of the info is still sent
    r = requests.get(f"https://shopgoodwill.com/item/{ID}", headers=headers)
    soup = bs4.BeautifulSoup(r.text, "html.parser")

    # If the title is just "Shopgoodwill" then it is the 404 page, return False
    if soup.find("title").text == "Shopgoodwill":
        return False

    title = soup.find("meta", property="og:title")["content"]
    description = soup.find("meta", property="og:description")["content"]
    image_url = soup.find("meta", property="og:image")["content"]

    # Extract price and end UNIX time
    scriptContent = soup.find("script", {"id": "serverApp-state"}).text

    re_price = re.compile(r"currentPrice&q;:([0-9\.]*)")
    price = re_price.findall(scriptContent)[0]

    re_remaining_time = re.compile(r"remainingTime&q;:&q;([0-9A-Za-z\ ]*)&q")
    remaining_time: str = re_remaining_time.findall(scriptContent)[0]
    # Get UNIX timestamp when listing ends
    end_timestamp = time_from_now(remaining_time)

    # Create listing object and add to database
    listing = Listing(ID, title, description, price, end_timestamp, image_url, False)
    db.add_listing(listing)

    return True


def fetch_listings_to_date(time_between_requests=2) -> None:
    """
    Fetches listings and insert them into the db
    Assumes find_first_listing() has run

    time_between_requests: Time in seconds between when each request should be issued,
    according to robots.txt 120 seconds should be used
    """
    global current_listing_ID
    while True:
        if fetch_listing(current_listing_ID):
            current_listing_ID += 1
            time.sleep(time_between_requests)
        else:
            break


def main() -> None:
    global current_listing_ID
    app.run(debug=True)
    current_listing_ID = find_first_listing(current_listing_ID)
    fetch_listings_to_date(time_between_requests=10)


if __name__ == "__main__":
    main()
