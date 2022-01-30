#!/usr/bin/env python

import datetime
import logging
import sys
import config
import cambot_utils as utils
import argparse
from collections import defaultdict, OrderedDict
import operator
import json
from math import factorial, ceil


def dynamic_playlist_updater(playlist_id):
    logging.info("Getting all user top tracks from all potential time frames. This is a lot of data so takes a second or two")
    top_tracks = {"7day"    :utils.user.get_top_tracks(period="7day", limit=100),
                  "1month"  :utils.user.get_top_tracks(period="1month", limit=100),
                  "3months" :utils.user.get_top_tracks(period="3month", limit=100),
                  "6months" :utils.user.get_top_tracks(period="6month", limit=100),
                  "12months":utils.user.get_top_tracks(period="12month", limit=100),
                  "overall" :utils.user.get_top_tracks(period="overall", limit=100)}

    logging.info("Done. Parsing information into a playlist ordered by weight. The more weight, the higher the song will be in the playlist")

    list_of_songs_and_their_weight = defaultdict(int)
    list_of_songs_and_their_total_plays = defaultdict(int)
    for timeframe, top_tracks_period in top_tracks.items():
        for track in top_tracks_period:
            track_and_artist = str(track[0])
            scrobbles = int(track[1])
            if list_of_songs_and_their_weight.get(track_and_artist, 0) == 0:
                # Add the song to the dict and add the first score
                list_of_songs_and_their_weight[track_and_artist] += ceil((calculate_song_weight(timeframe, scrobbles)))
                list_of_songs_and_their_total_plays[track_and_artist] += scrobbles
            else:
                # This song is already in the list. Minus the scrobbles that have already been counted. Because the program is single threaded we can assume the program runs in timeframe descending
                current_amount_of_scrobbles = list_of_songs_and_their_total_plays[track_and_artist]
                list_of_songs_and_their_weight[track_and_artist] += ceil((calculate_song_weight(timeframe, scrobbles - current_amount_of_scrobbles)))

    sorted_tracks = OrderedDict(
        sorted(list_of_songs_and_their_weight.items(), key=operator.itemgetter(1), reverse=True))

    # Print out to the console the weighting each song has, for research purposes
    logging.info(json.dumps(sorted_tracks, indent=4))
    
    if TESTING:
        logging.info("testing mode enabled. Exiting program before updating platlist")
        sys.exit()

    # Get a list of tracks from sorted list
    spotify_searched_tracks = []
    twitter_summary_tracks = []
    limit = 0
    for key, value in sorted_tracks.items():
        if limit < 100:
            search = utils.search_spotify(utils.sp, key, "track")
            if search is not None:
                spotify_searched_tracks.append(search)
                limit += 1
        else:
            break

    logging.info("Updating spotify playlist and description")
    utils.sp.playlist_replace_items(playlist_id, spotify_searched_tracks)
    # Update the playlist description to show when the playlist was last updated
    utils.sp.playlist_change_details(playlist_id,
                            description=" Last updated - {} - {}".format(datetime.date.today(),
                                                                            config.rhitons_selection_description))

def calculate_song_weight(timeframe, scrobbles):
    # TODO: BIG TODO: FIGURE OUT A WEIGHTING SYSTEM. user enters weight based on lower/higher number being more long term based. Output a score! Why is that so hard
    # Last 7 days
    if "7day" in timeframe:
        return 400 * scrobbles 
    # Last month
    elif "1month" in timeframe:
        return 200 * scrobbles
    # Last 3 months
    elif "3months" in timeframe:
        return 150 * scrobbles
    # Last 6 months
    elif "6months" in timeframe:
        return 80 * scrobbles
    # Last year
    elif "12months" in timeframe:
        return 60 * scrobbles
    # Overall
    elif "overall" in timeframe:
        return 30 * scrobbles

def check_number(value):
    ivalue = int(value)
    if ivalue <= 0 or ivalue > 10:
        raise argparse.ArgumentTypeError("%s is an invalid int value. The limit is between 1 and 10" % value)
    return ivalue


parser = argparse.ArgumentParser()
parser.add_argument("--id", help="Playlist ID to update", required=True)
parser.add_argument("--weighting", "-w", type=check_number, help="A number between 1-10 that tells the dynamic playlister which time frames to give more bearing to. For instance, a value of 9 will give songs that have been played a lot over the years more score than those songs that have been discovered by the user more recently and played a lot but have no scrobbles from the long term timeframe. A value of 1 will output a playlist more atuned to songs that have been played recently.", default=5)
parser.add_argument("--testing", help="Flag enables no updates to the spotify playlist / tweets.", action="store_true")
args = parser.parse_args()

SCORE_WEIGHTING = args.weighting
TESTING = False
if args.testing:
    logging.info("Testing mode")
    TESTING = True

dynamic_playlist_updater(str(args.id))
