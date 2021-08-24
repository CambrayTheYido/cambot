#!/usr/bin/env python
import datetime

import spotipy
from twython import Twython
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
from spotipy.oauth2 import SpotifyOAuth
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
# token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
#                                    redirect_uri="http://localhost:8090", scope=scope)
# Spotify Token
CACHE = ".cache-" + "test"
spotify_client_id="8e62289bbb4e4d029993378b17ede367"
spotfiy_client_secret="9e398cc0a837401fb19550eb3918281f"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path=CACHE, client_secret=spotfiy_client_secret, client_id=spotify_client_id, redirect_uri="http://localhost:8080"))


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
        artist = track['artists'][0].get('name')
        if artist not in some_artists:
            some_artists.append(artist)

        list_of_tracks_to_add.append(track['uri'])

    sp.user_playlist_add_tracks(user=spotify_username, playlist_id=playlist_id, tracks=list_of_tracks_to_add)

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

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--timeframe",
                    help="Creates a playlist of the top songs from the past month, 6 months or years.",
                    choices=['short_term', 'medium_term', 'long_term'])
parser.add_argument("--limit", help="Specify how many tracks you want in the playlist", default=50, type=check_number)
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

if add == 'add':
    print("adding artist names to the database.", flush=True)
    add_to_database = True

if tweet:
    print("TEST MODE: not tweeting to the account provided")
    TWEET = False

create_playlist(time_range, limit)
