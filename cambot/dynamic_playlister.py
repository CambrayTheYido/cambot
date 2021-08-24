#!/usr/bin/env python
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

# Spotify API
scope = "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private streaming ugc-image-upload user-follow-modify user-follow-read user-library-read user-library-modify user-read-private user-read-birthdate user-read-email user-top-read user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played"
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify Token
CACHE = ".cache-" + "test"
spotify_client_id="8e62289bbb4e4d029993378b17ede367"
spotfiy_client_secret="9e398cc0a837401fb19550eb3918281f"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path=CACHE, client_secret=spotfiy_client_secret, client_id=spotify_client_id, redirect_uri="http://localhost:8888/callback"))


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
    sorted_tracks = OrderedDict(sorted(list_of_songs_and_their_weight.items(), key=operator.itemgetter(1), reverse=True))

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

    tracks_to_remove = []
    tracks_to_add = []

    playlist = sp.playlist_tracks(playlist_id=playlist_id)
    # order = 0
    # for item in playlist['items']:
    #     link = item["external_urls"].get("url")
    #     if link not in spotify_searched_tracks:
    #         # Remove from playlist at end
    #         tracks_to_remove.append(link)
    sp.user_playlist_replace_tracks(spotify_username,playlist_id,spotify_searched_tracks)


    #sp.user_playlist_remove_all_occurrences_of_tracks(user=spotify_username, playlist_id=playlist_id, tracks=tracks_to_remove)



def calculate_song_weight(reference_count):
    if reference_count == 1:
        return 200
    elif reference_count == 2:
        return 90
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
