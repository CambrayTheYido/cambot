#!/usr/bin/env python
import sys
sys.path.append("/cambot/")
import spotipy
import spotipy.util as util
import config
from cambot import twitter_handles as t
import pylast
import pymongo
import argparse
from collections import defaultdict, OrderedDict
import operator

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

def dynamic_playlist_updater(playlist_id):
    # Start with getting the top songs for each artist stored in the database
    mydb = myclient["artist"]
    mycol = mydb["collection"]

    top_tracks = [user.get_top_tracks(period="7day"),
                  user.get_top_tracks(period="1month"),
                  user.get_top_tracks(period="3month"),
                  user.get_top_tracks(period="6month"),
                  user.get_top_tracks(period="12month"),
                  user.get_top_tracks(period="overall")]

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
    reference_count = 1
    sorted_tracks = OrderedDict(sorted(list_of_songs_and_their_weight.items(), key=operator.itemgetter(1), reverse=True))

    if token:
        sp = spotipy.Spotify(auth=token)


        # Get a list of tracks from sorted list
        spotify_searched_tracks = []
        limit = 0
        for key, value in sorted_tracks.items():
            if limit < 50:
                search = t.search_spotify(sp, key, "track")
                if search is not None:
                    spotify_searched_tracks.append(search)
                    limit += 1
            else:
                break

        tracks_to_remove = []
        tracks_to_add = []

        playlist = sp.user_playlist_tracks(user=spotify_username, playlist_id=playlist_id)
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
        points_per_hit = 200
    elif reference_count == 2:
        points_per_hit = 90
    elif reference_count == 3:
        points_per_hit = 35
    elif reference_count == 4:
        points_per_hit = 15
    elif reference_count == 5:
        points_per_hit = 7
    elif reference_count == 6:
        points_per_hit = 5
    return points_per_hit

parser = argparse.ArgumentParser()
parser.add_argument("--id", help="Playlist ID to update")
args = parser.parse_args()

dynamic_playlist_updater(args.id)