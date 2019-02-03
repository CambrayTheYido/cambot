#!/usr/bin/env python
import datetime
import operator

import spotipy
from twython import Twython
import spotipy.util as util
import config
import twitter_handles as t
import argparse
import pylast
import pymongo
from collections import defaultdict, OrderedDict

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

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

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

add_to_database = False
TWEET = True


def get_current_month():
    now = datetime.datetime.now()
    month = now.month
    if (month == 1):
        month = "December"
    elif (month == 2):
        month = "January"
    elif (month == 3):
        month = "February"
    elif (month == 4):
        month = "March"
    elif (month == 5):
        month = "April"
    elif (month == 6):
        month = "May"
    elif (month == 7):
        month = "June"
    elif (month == 8):
        month = "July"
    elif (month == 9):
        month = "August"
    elif (month == 10):
        month = "September"
    elif (month == 11):
        month = "October"
    elif (month == 12):
        month = "November"
    return month


def get_correct_year():
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    if month == 1:
        return year - 1
    return year


def turn_time_range_into_english_sentence(time_range):
    if time_range == 'short_term':
        time_range = get_current_month()
    elif time_range == 'medium_term':
        time_range = "the last 6 months"
    else:
        time_range = "the last few years"
    return time_range


def create_playlist(time_range, limit):
    if time_range == 'short_term':
        playlist_name = "Top tracks of {} {}".format(get_current_month(), get_correct_year())
    elif time_range == 'medium_term':
        playlist_name = "Top tracks of the last 6 months as of {} {}".format(get_current_month(),
                                                                             get_correct_year())
    else:
        playlist_name = "Top tracks over the last few years as of {} {}".format(get_current_month(),
                                                                                get_correct_year())

    if token:
        sp = spotipy.Spotify(auth=token)

        # Create a new playlist
        playlist = sp.user_playlist_create(user=spotify_username, name=playlist_name, public=True)
        playlist_id = playlist.get('uri')

        # Get top tracks from the chosen time range and the limit
        top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=limit)

        list_of_tracks_to_add = []
        some_artists = []

        # Iterate through the tracks to get the relevant information
        for track in top_tracks['items']:

            # Store a list of artists to involve in the tweet
            artist = t.check_or_add_artist_names_to_database(track['artists'][0].get('name'), add_to_database)
            if artist not in some_artists:
                some_artists.append(artist)

            list_of_tracks_to_add.append(track['uri'])

        sp.user_playlist_add_tracks(user=spotify_username, playlist_id=playlist_id, tracks=list_of_tracks_to_add)
    else:
        print("Can't get token for", spotify_username)

    playlist_link_url = playlist['external_urls']
    playlist_link_url = playlist_link_url.get('spotify')
    tweet_str = "Here's a spotify playlist of my most listened to songs in {}\n{}\n\nThis includes artists such as: ".format(
        turn_time_range_into_english_sentence(time_range), playlist_link_url)
    for artist in some_artists:
        if len(tweet_str) + len(artist) <= 280:
            tweet_str += artist + ", "
    tweet_str = tweet_str[:-2] + "."
    print(tweet_str)
    if TWEET:
        api.update_status(status=tweet_str)


def check_number(value):
    ivalue = int(value)
    if ivalue <= 0 or ivalue > 50:
        raise argparse.ArgumentTypeError("%s is an invalid int value. The limit is between 1 and 50" % value)
    return ivalue


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

    # Loop over all the artists in the database
    collection_of_artists = mycol.find()
    for artist in collection_of_artists:
        # Find this artist in each top songs list. Shorter time frame listens count as a higher point score than one from
        # a time period that is longer. E.g. 1 listen from the 7day period = 100 points. 1 listen from 1 month period = 60 and so on
        artist_name = artist["name"]
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
parser.add_argument("-t", "--timeframe",
                    help="Creates a playlist of the top songs from the past month, 6 months or years.",
                    choices=['short_term', 'medium_term', 'long_term'])
parser.add_argument("--limit", help="Specify how many tracks you want in the playlist", default=50, type=check_number)
parser.add_argument("-d", "--dynamic", help="Runs the dynamic playlist updater.", default="09mHNJgzOgdUZksMrohoPH")
parser.add_argument("--tweet",
                    help="If this has been entered, then the script will NOT tweet to the account provided.",
                    action="store_true")
parser.add_argument("-a", "--at",
                    help="Include this at runtime to replace mentions of artists names with their twitter handles. If add is selected, you will be prompted to enter twitter handles of the corresponding artist if it was not found in the database.",
                    default="leave", choices=['add', 'leave'])
args = parser.parse_args()

time_range = args.timeframe
limit = int(args.limit)
add = args.at
tweet = args.tweet
dynamic = args.dynamic

if add == 'add':
    print("adding artist names to the database.", flush=True)
    add_to_database = True

if tweet:
    print("TEST MODE: not tweeting to the account provided")
    TWEET = False

if dynamic:
    print("Dynamic playlist mode selected", flush=True)
    dynamic_playlist_updater(dynamic)
else:
    create_playlist(time_range, limit)
