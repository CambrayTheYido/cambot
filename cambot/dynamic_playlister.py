#!/usr/bin/env python
import datetime
import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import config
import twitter_handles as t
import pylast
import pymongo
import argparse
from collections import defaultdict, OrderedDict
import operator
import json

# Spotify API
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotify_client_secret
scope = config.spotify_scope

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify Token
CACHE = ".cache-" + "test"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(scope=scope, cache_path=CACHE, client_secret=client_secret, client_id=client_id,
                              redirect_uri="http://localhost:8888/callback"))

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)


def dynamic_playlist_updater(playlist_id):
    top_tracks = [user.get_top_tracks(period="7day", limit=500),
                  user.get_top_tracks(period="1month", limit=500),
                  user.get_top_tracks(period="3month", limit=500),
                  user.get_top_tracks(period="6month", limit=500),
                  user.get_top_tracks(period="12month", limit=500),
                  user.get_top_tracks(period="overall", limit=500)]

    # TODO: user.getRecentTracks with time_ranges. Use same time range song weights. e.g. 1 week all 100 for each hit. 1 month (minus that week thats already been counted)

    reference_count = 1
    list_of_songs_and_their_weight = defaultdict(int)
    for period_top_tracks_list in top_tracks:
        for track in period_top_tracks_list:
            track_and_artist = str(track[0])
            scrobbles = int(track[1])
            # Add the song to the dict if not exist, and either way update that songs weighting
            list_of_songs_and_their_weight[track_and_artist] += (calculate_song_weight(reference_count) * scrobbles)
        reference_count += 1
    sorted_tracks = OrderedDict(
        sorted(list_of_songs_and_their_weight.items(), key=operator.itemgetter(1), reverse=True))

    # Print out to the console the weighting each song has, for research purposes
    print(json.dumps(sorted_tracks, indent=4), flush=True)

    # Get a list of tracks from sorted list
    spotify_searched_tracks = []
    limit = 0
    for key, value in sorted_tracks.items():
        if limit < 100:
            search = t.search_spotify(sp, key, "track")
            if search is not None:
                spotify_searched_tracks.append(search)
                limit += 1
        else:
            break

    sp.playlist_replace_items(playlist_id, spotify_searched_tracks)
    # Update the playlist description to show when the playlist was last updated
    sp.playlist_change_details(playlist_id,
                               description=" Last updated - {} - {}".format(datetime.date.today(),
                                                                            config.rhitons_selection_description))

    # sp.user_playlist_remove_all_occurrences_of_tracks(user=spotify_username, playlist_id=playlist_id, tracks=tracks_to_remove)


def calculate_song_weight(reference_count):
    if reference_count == 1:
        return 250
    elif reference_count == 2:
        return 110
    elif reference_count == 3:
        return 50
    elif reference_count == 4:
        return 30
    elif reference_count == 5:
        return 20
    elif reference_count == 6:
        return 12


parser = argparse.ArgumentParser()
parser.add_argument("--id", help="Playlist ID to update")
args = parser.parse_args()

dynamic_playlist_updater(str(args.id))
