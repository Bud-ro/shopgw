from flask import Flask
from flask import escape
import apprise
from os import environ
from store import Store
import requests
import bs4

# Global variables
current_listing_ID = 141163191 # Can set to approximate start or or None
# Gets overwritten if .config file exists
filter_list = ["record", "vinyl", "LP", "cassette", "beta", "laser disk"]

# Load .env
DISCORD_WEBHOOK_LINK = environ.get("DISCORD_WEBHOOK_LINK")
DATABASE = "listings.sqlite" # Located in local directory
db = Store(DATABASE)

app = Flask(__name__)
apobj = apprise.Apprise()
apobj.add(DISCORD_WEBHOOK_LINK)

@app.route("/")
def index():
    return f"Apprise link: {DISCORD_WEBHOOK_LINK}"

@app.route("/db")
def db_test():
    return db.get_listings()

def setup():
    """
    Initializes our app by finding the oldest listing that is still active.
    This then sets our {current_listing_ID} to that.
    """
    app.logger.info("Running setup")
    # TODO: Find oldest active listing
    pass

@app.route("/listing/<int:ID>")
def fetch_listing(ID):
    """
    Requests https://shopgoodwill.com/item/{ID} and scrapes for information using bs4
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    # Doesn't fully load the page, so pricing information is missing
    r = requests.get(f"https://shopgoodwill.com/item/{ID}", headers=headers)
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    title = soup.find("meta", property="og:title")["content"]
    return title

def fetch_listings_to_date(time_between_requests=2):
    """
    Fetches listings and insert them into the db
    Assumes setup() has run

    time_between_requests: Time in seconds between when each request should be issued
    """
    global current_listing_ID
    while True:
        listing = fetch_listing(current_listing_ID)
        if not listing is None:
            db.add_listing(*listing) # Unpacks tuple
        else:
            return
    pass

def main():
    setup()
    # fetch_listings_to_date(time_between_requests=10)
    app.run(debug=True)

if __name__ == "__main__":
    main()