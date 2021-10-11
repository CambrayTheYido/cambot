#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import logging
import cambot_utils as utils
import argparse
from datetime import datetime, timedelta
import time
import sys
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def check_date(date):
    if date is not None:
        date_today = datetime.now()
        try:
            date_and_time_split = date.split("-", maxsplit=4)
            timestamp = datetime(year=int(date_and_time_split[0]), month=int(date_and_time_split[1]), day=int(date_and_time_split[2]), 
                        hour=int(date_and_time_split[3]), minute=int(date_and_time_split[4]))
        except IndexError as e:
            logging.error("Incorrect timestamp format. User input timestamp should be in the format 'YYYY-MM-DD-HH-MM-SS'")
            logging.error(e)
        if timestamp > date_today or timestamp < timestamp - timedelta(days=14):
            logging.error("Cannot scrobble this date. Either it is in the future or over two weeks ago from current datetime. Please enter a suitable timestamp")
            raise argparse.ArgumentError
        # Convert date time into timestamp as lastfm takes UNIX time
        return int(datetime.timestamp(timestamp))
    else:
        return int(time.time())

def clean_artist_string(artist):
    if "ft." in artist:
        logging.info("Removing the ft. artist from artist string [{}]. We only need the one artist to keep scrobbles consitent across platforms".format(artist))
        return artist.split("ft.")[0].strip()
    return artist

def parse_url(tracklist):
    r = requests.get(tracklist, headers={'User-Agent': UserAgent().firefox })
    soup = BeautifulSoup(r.text, features="html.parser")

    for track in soup.find_all("div", itemprop="tracks"):
        track = track.find(itemprop="name")['content']
        if track is not None:
            parse_file_line(track)


def parse_file_line(track):
    if " - " not in track:
        logging.warn("Track - [{}] - cannot be scrobbled. Incorrect format".format(track))
        return

    track_split = track.split(" - ", maxsplit=1)
    if reverse:
        artist = clean_artist_string(track_split[-1].strip)()
        trackname = track_split[0].strip()
        scrobble({"artist":artist, "trackname":trackname})
    else:
        trackname = track_split[-1].strip()
        artist = clean_artist_string(track_split[0].strip())
        scrobble({"artist":artist, "trackname":trackname})


def scrobble(track):
    artist = track["artist"]
    trackname = track["trackname"]
    timestamp = check_date(date)

    logging.info("Attempting to scrobble...")
    logging.info("Artist: {}".format(artist))
    logging.info("Track: {}".format(trackname))
    logging.info("Timestamp: {} / {}".format(timestamp, datetime.fromtimestamp(timestamp)))

    global num_errors
    global total_tracks_scrobbled

    try:
        if not test:
            if num_errors < 5:
                utils.network.scrobble(artist=artist, title=trackname, timestamp=timestamp)
                total_tracks_scrobbled += 1
            else:
                logging.info("Failed 3 times already. Repeated scrobbles might see us get a temp IP ban so best not waste requests when they are failing. Stop for now!")
    except utils.pylast.MalformedResponseError as e:
        logging.error("Unable to scrobble '{}'".format(track))
        logging.error(e)
        num_errors += 1

    if num_errors > 5:
        logging.warning("Shutting down.")
        sys.exit()

    logging.info("--------------------------------------------------------")


parser = argparse.ArgumentParser()
parser.add_argument("--file", help="A text file that contains the songs you want to scrobble in '%Artist%' - '%Name%' format with each scrobble on a newline")
parser.add_argument("--tracklist", help="A link to 1001tracklists that will parse the tracklist and scrobble all songs on the list")
parser.add_argument("--timestamp", "-t", help="Timestamp of when the song(s) were actually scrobbled. In the format 'YYYY-MM-DD-HH-MM'. You cannot scrobble anything in the future or anything over 2 weeks ago")
parser.add_argument("--reverse", help="If the tracklist is stored in the format of '%track% - %artist'", action="store_true")
parser.add_argument("--test", help="Testing. Do not scrobble", action="store_true")
args = parser.parse_args()

file = args.file
tracklist = args.tracklist
if not file and not tracklist:
    logging.error("Please supply either a tracklist from a file or a URL to 1001tracklists")
    raise argparse.ArgumentError
if file and tracklist:
    logging.error("Can't parse both a file and a tracklist. Please only use one of these required parameters")
    raise argparse.ArgumentError

reverse = args.reverse
test = args.test
date = args.timestamp

num_errors = 0
total_tracks_scrobbled = 0

if reverse:
    logging.info("Treating tracklist in %track% - %artist% format")
if test:
    logging.info("Test mode. Will not scrobble")

if tracklist:
    parse_url(tracklist)
else:    
    with open(file) as tracklist:
        for track in tracklist:
            parse_file_line(track)
