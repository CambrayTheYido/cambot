#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import logging
import config
import cambot_utils as utils
import argparse
from datetime import datetime, timedelta
import time
import sys


def check_syntax(track):
    if "-" not in track:
        logging.warn(
            "Track - [{}] - cannot be scrobbled. Incorrect format".format(track))
        return
    track_split = track.split("-", maxsplit=1)
    artist = None
    trackname = None
    timestamp = None
    if reverse:
        artist = track_split[-1].strip()
        trackname = track_split[0].strip()
    else:
        trackname = track_split[-1].strip()
        artist = track_split[0].strip()

    if date is not None:
        date_today = datetime.now()
        try:
            date_str = date.split("-", maxsplit=3)
            time_str = date.split(" ", maxsplit=1)
            timestamp = datetime(year=int(date_str[0]), month=int(date_str[1]), day=int(date_str[2], 
                        hour=int(time_str[1].split("-")[0], minute=int(time_str[1].split("-")[1]))))
        except IndexError as e:
            logging.error(
                "Incorrect timestamp format. User input timestamp should be in the format 'YYYY-MM-DD HH-MM-SS'")
            logging.error(e)
        if timestamp > date_today or timestamp < timestamp - timedelta(days=14):
            logging.error(
                "Cannot scrobble this date. Either it is in the future or over two weeks ago from current datetime. Please enter a suitable timestamp")
            raise argparse.ArgumentError
        # Convert date time into timestamp as lastfm takes UNIX time
        timestamp = int(datetime.timestamp(timestamp))
    else:
        timestamp = int(time.time())

    logging.info("Attempting to scrobble '{}'".format(track))
    logging.info("Artist: {}".format(artist))
    logging.info("Track: {}".format(trackname))
    logging.info("Timestamp: {}".format(timestamp))

    global num_errors

    try:
        if not test:
            if num_errors < 2:
                utils.network.scrobble(artist=artist, title=trackname, timestamp=timestamp)
            else:
                logging.info("Failed 3 times already. Repeated scrobbles might see us get a temp IP ban. Stop for now!")
                logging.warning("Shutting down.")
                sys.exit()
    except SystemExit:
        sys.exit()
    except utils.pylast.MalformedResponseError as e:
        logging.error("Unable to scrobble '{}'".format(track))
        logging.error(e)
        num_errors += 1


parser = argparse.ArgumentParser()
parser.add_argument(
    "--file", help="A text file that contains the songs you want to scrobble in '%Artist%' - '%Name%' format with each scrobble on a newline", required=True)
parser.add_argument("--timestamp", "-t", help="Timestamp of when the song(s) were actually scrobbled. In the format 'YYYY-MM-DD HH-MM'. You cannot scrobble anything in the future or anything over 2 weeks ago")
parser.add_argument(
    "--reverse", help="If the tracklist is stored in the format of '%track% - %artist'", action="store_true")
parser.add_argument(
    "--test", help="Testing. Do not scrobble", action="store_true")
args = parser.parse_args()

file = args.file
reverse = args.reverse
test = args.test
date = args.timestamp

num_errors = 0

if reverse:
    logging.info("Treating track list in %track% - %artist% format")
if test:
    logging.info("Test mode. Will not scrobble")

with open(file) as tracklist:
    for track in tracklist:
        check_syntax(track)
