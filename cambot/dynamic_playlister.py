#!/usr/bin/env python

import datetime
import logging
import config
import cambot_utils as utils
import argparse
from collections import defaultdict, OrderedDict
import operator
import json
from math import factorial, ceil


def dynamic_playlist_updater(playlist_id):
    logging.info("Getting all user top tracks from all potential time frames. This is a lot of data so takes a second or two")
    top_tracks = [utils.user.get_top_tracks(period="7day", limit=100),
                  utils.user.get_top_tracks(period="1month", limit=100),
                  utils.user.get_top_tracks(period="3month", limit=100),
                  utils.user.get_top_tracks(period="6month", limit=100),
                  utils.user.get_top_tracks(period="12month", limit=100),
                  utils.user.get_top_tracks(period="overall", limit=100)]

    # TODO: user.getRecentTracks with time_ranges. Use same time range song weights. e.g. 1 week all 100 for each hit. 1 month (minus that week thats already been counted)

    reference_count = 1
    list_of_songs_and_their_weight = defaultdict(int)
    for period_top_tracks_list in top_tracks:
        for track in period_top_tracks_list:
            track_and_artist = str(track[0])
            scrobbles = int(track[1])
            # Add the song to the dict if not exist, and either way update that songs weighting
            list_of_songs_and_their_weight[track_and_artist] += ceil((calculate_song_weight(reference_count) * scrobbles))
        reference_count += 1
    sorted_tracks = OrderedDict(
        sorted(list_of_songs_and_their_weight.items(), key=operator.itemgetter(1), reverse=True))

    # Print out to the console the weighting each song has, for research purposes
    logging.info(json.dumps(sorted_tracks, indent=4))

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
    if not TESTING:
        logging.info("Updating spotify playlist and description")
        utils.sp.playlist_replace_items(playlist_id, spotify_searched_tracks)
        # Update the playlist description to show when the playlist was last updated
        utils.sp.playlist_change_details(playlist_id,
                               description=" Last updated - {} - {}".format(datetime.date.today(),
                                                                            config.rhitons_selection_description))
    else:
        logging.info("Did not update the playlist. Testing flag enabled")

def calculate_song_weight(reference_count):
    # Last 7 days
    if reference_count == 1:
        return SCORE_WEIGHTING * 100
    # Last month
    elif reference_count == 2:
        return (SCORE_WEIGHTING / reference_count) * 80
    # Last 3 months
    elif reference_count == 3:
        return (SCORE_WEIGHTING / reference_count) * 64
    # Last 6 months
    elif reference_count == 4:
        return (SCORE_WEIGHTING / reference_count) * 53
    # Last year
    elif reference_count == 5:
        return (SCORE_WEIGHTING / reference_count) * 42
    # Overall
    elif reference_count == 6:
        return (SCORE_WEIGHTING / reference_count) * 34

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
