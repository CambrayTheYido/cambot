#!/usr/bin/env python
'''Script that scrapes a bandcamp profile page and stores information on all the purchased items.
If the script is run with the update flag, then any new additions to the users
collection is tweeted'''

import os
import logging
import argparse
import cambot_utils as utils

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

URL = "https://bandcamp.com/"
PROFILE_TO_SCRAPE = os.environ.get("BANDCAMP_PROFILE_USERNAME")
UPDATE_DB_ONLY = False


def main():
    args = parse_args()
    UPDATE_DB_ONLY = args.update

    logging.info("%s", UPDATE_DB_ONLY)

    scrape_bandcamp_profile()


def scrape_bandcamp_profile():
    """Parse a URL and loop over each track and submit the artist and track to the scrobble method"""
    bandcamp_profile_url = URL + str(PROFILE_TO_SCRAPE)
    logging.info("Parsing URL: %s",bandcamp_profile_url)
    r = requests.get(bandcamp_profile_url, headers={"User-Agent": UserAgent().firefox})
    soup = BeautifulSoup(r.text, features="html.parser")
    logging.debug("SOUP: %s", soup)

    # TODO: Look into lazy loading the rest of the collection. For now this is ok if a user buys
    # less than 20 items since the update has run!
    for collection_item in soup.find_all("div", class_="collection-title-details"):
        track_url = collection_item.find("a", class_="item-link").get("href")
        track_name = collection_item.find("div", class_="collection-item-title")
        .get_text().replace("(gift given)", "").strip()
        artist_name = collection_item.find("div", class_="collection-item-artist").get_text()
        logging.info("Artist: %s | Track: %s | URL: %s", artist_name, track_name, track_url)
        update_db_and_tweet_if_new(track_name, artist_name, track_url)

def update_db_and_tweet_if_new(track_name, artist_name, track_url):
    """Lookup if the bandcamp track URL is in the DB. If it is not then add
    and tweet the update"""
    mydb = utils.myclient["bandcamp"]
    mycol = mydb["collection"]

    if mycol.find_one({"track_url": track_url.lower()}) is None:
        logging.info("""New item in the users collection. Add to the db and tweet
         if user granted permission""")
        add = {"track_url": track_url}
        mycol.insert_one(add)
        logging.info("Succesfully added %s %s to the database", track_name, artist_name)

        if not UPDATE_DB_ONLY:
            tweet = """🛒 Just bought {} {} on bandcamp 🎵
                
{}""".format(track_name, artist_name, track_url)
            logging.info("Tweeting: %s", tweet)
            utils.api.update_status(status=tweet)
    else:
        logging.info("""Item {} {} already in the database. No update required and 
        moving onto the next item in the collection""".format(track_name, artist_name))

def parse_args():
    """Parse the arguments entered by the user and return the args namespace"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", 
                        help="""Flag that is used to just update the DB and tweet any new 
                            additions to the users collection""",
                        action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    main()