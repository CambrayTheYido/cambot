#!/usr/bin/env python
import pylast
from twython import Twython
import argparse
import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import twitter_handles
import datetime
from dateutil.relativedelta import *
from time import sleep
import os
import pymongo
from math import ceil

# PyMongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify Token
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=config.spotify_scope, client_secret=config.spotify_client_secret, client_id=config.spotify_client_id, redirect_uri="http://localhost:8888/callback"))

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

age_of_account_in_years_months = datetime.datetime.utcfromtimestamp(int(user.get_registered())).strftime('%Y-%m-%d')

age_of_account_in_years_months = datetime.date(int(age_of_account_in_years_months.split('-')[0]),
                                               int(age_of_account_in_years_months.split('-')[1]),
                                               int(age_of_account_in_years_months.split('-')[2]))

age_of_account_in_years_months = str(relativedelta(datetime.date.today(), age_of_account_in_years_months).years) + \
                                 ' years and ' + str(
    relativedelta(datetime.date.today(), age_of_account_in_years_months).months) \
                                 + ' months'

time_frames = {'7day': 'week',
               '1month': 'month',
               '3month': '3 months',
               '6month': '6 months',
               '12month': 'year',
               # leave overall blank and work out length using age of account
               'overall': age_of_account_in_years_months}

PLAYS = " plays\n"

tweet = True
add_to_database = False

NO_UPDATE_NEEDED = "Information up to date and already tweeted."


def get_latest_tweet():
    the_latest_tweet = None
    while the_latest_tweet is None:
        the_latest_tweet = api.get_user_timeline(screen_name="BotCambray")
        the_latest_tweet = the_latest_tweet[0].get('id')
    return the_latest_tweet

def get_relevant_time_frame_information(type, time_frame):
    if time_frame == "7day":
        return "New #Top{}Update of the week".format(type.title(), time_frame)
    elif time_frame == "1month":
        return "New #Top{}Update of the month".format(type.title(), time_frame)
    elif time_frame == "3month":
        return "New #Top{}Update of the last 3 months".format(type.title(), time_frame)
    elif time_frame == "6month":
        return "New #Top{}Update of the last 6 months".format(type.title(), time_frame)
    elif time_frame == "12month":
        return "New #Top{}Update of the last year".format(type.title(), time_frame)
    elif time_frame == "overall":
        return "New #Top{}Update of all time ({})".format(type.title(), age_of_account_in_years_months)
    return

def singular_top_update(period, top, type):
    x = top[0]
    search_str = str(x[0])
    if type == "track":
        tweetable_string = replace_top_item_artist_with_handle(x)
    if type == "album":
        tweetable_string = str(search_str.split("-")[1]).strip()
    else:
        tweetable_string = twitter_handles.check_or_add_artist_names_to_database(search_str, add_to_database)

    mydb = myclient["artist_names"]
    mycol = mydb["singular_top_update"]

    mongo_search_term = {"type":type, "period":period}

    if mycol.find_one(mongo_search_term) != None:
        mongo_return = mycol.find_one(mongo_search_term)

        if mongo_return["value"] != search_str:
            update_mongo = { "$set": {"value": search_str, "timestamp": datetime.datetime.utcnow()}}
            # Get the timestamp from the previous update first though
            timestamp_from_last_update = mongo_return["timestamp"]
            last_update_string = mongo_return["value"]

            try:
                item_url = search_spotify(search_str, type)
                how_long_item_was_top_days = abs((datetime.datetime.utcnow() - timestamp_from_last_update).days)
                how_long_item_was_top_hours = ceil((datetime.datetime.utcnow() - timestamp_from_last_update).seconds / 3600 % 24)
                tweetStr = "{} \n\n{} \n\nThis replaces the previous top {} '{}' which stood for {} days {} hours \n{}".format(get_relevant_time_frame_information(type, period), tweetable_string, type, last_update_string, str(how_long_item_was_top_days), str(how_long_item_was_top_hours), str(item_url))
                print(tweetStr, flush=True)
                if tweet:
                    api.update_status(status=tweetStr)
                    mycol.update_one(mongo_search_term, update_mongo)
                    # Just to reduce the spam load a little.
                    sleep(5)
            except:
                print("Could not tweet latest {} update".format(type), flush=True)
        else:
            print("No update needed for {} {}".format(type, period))

    else:
        mycol.insert_one({"type":type, "period": period, "value": search_str, "timestamp": datetime.datetime.utcnow()})
        # Try that again!
        print("Recursion!")
        singular_top_update(period, top, type)
        return


def gather_relevant_information(type, time_frame, limit):
    if type == 'artist':
        # determine period to use
        top = user.get_top_artists(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Artists of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            # Tweet the first tweet to get the ball rolling, grab the ID of the tweet while we're at it
            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            # Now we can chain the following tweets onto the first tweet
            chain_updates(top, latest_tweet, type)
        else:
            singular_top_update(time_frame, top, type)

    elif type == 'track':
        top = user.get_top_tracks(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Tracks of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            chain_updates(top, latest_tweet, type)
        else:
            singular_top_update(time_frame, top, type)

    elif type == 'album':
        top = user.get_top_albums(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Albums of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            chain_updates(top, latest_tweet, type)
        else:
            singular_top_update(time_frame, top, type)

def search_spotify(search_string, type):
    result = sp.search(search_string, limit='1', type=type)
    if type == 'artist':
        result = result['artists']['items']
    elif type == 'track':
        result = result['tracks']['items']
    elif type == 'album':
        result = result['albums']['items']
    url = ''
    for item in result:
        url = item['external_urls']
        url = url.get('spotify')
    if url == '':
        print('No results found in spotify search for {}'.format(search_string), flush=True)
    return url

# Pass the top item list
def replace_top_item_artist_with_handle(top_item):
    top_item_split = str(top_item[0]).split('-', maxsplit=1)
    rest_of_split = str(top_item_split[1])
    artist_extract = str(top_item_split[0]).strip()
    artist_extract = twitter_handles.check_or_add_artist_names_to_database(artist_extract, add_to_database)
    return str(artist_extract) + " -" + str(rest_of_split)

def chain_updates(list_of_top_items, latest_tweet, type):
    tweet_count = 1
    for top_item in list_of_top_items:
        track_artist_album_search = str(top_item[0])

        # For tracks and albums, we need to extract the part which is the artist and then replace with their handle
        if type == 'track' or type == 'album' and include_twitter_handles:
            track_artist_album = replace_top_item_artist_with_handle(top_item)
        else:
            track_artist_album = str(top_item[0])
            if include_twitter_handles and type == 'artist':
                track_artist_album = twitter_handles.check_or_add_artist_names_to_database(track_artist_album, add_to_database)
        playcount = str(top_item[1])

        add_to_tweet = "{}. {} - {}{} \n{}".format(tweet_count, track_artist_album, playcount, PLAYS,
                                                   search_spotify(track_artist_album_search, type))
        if tweet and add_to_tweet != 'True':

            api.update_status(status=add_to_tweet, in_reply_to_status_id=latest_tweet)
            latest_tweet = get_latest_tweet()
            sleep(30)

        print(add_to_tweet, flush=True)

        tweet_count += 1
        if tweet_count > limit:
            break

def check_number(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid int value. The minimum value has to be one or more" % value)
    return ivalue


choices = ["7day", "1month", "3month", "6month", "12month", "overall", "all"]

parser = argparse.ArgumentParser()
parser.add_argument("--tracks",
                    help="Tweets the top tracks from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script", choices=choices)
parser.add_argument("--albums",
                    help="Tweets the top albums from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script",
                    choices=choices)
parser.add_argument("--artists",
                    help="Tweets the top artists from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script",
                    choices=choices)
parser.add_argument("-a", "--at",
                    help="Include this at runtime to replace mentions of artists names with their twitter handles. If add is selected, you will be prompted to enter twitter handles of the corresponding artist if it was not found in the database.", choices=['add', 'leave'])
parser.add_argument("-t", "--tweet",
                    help="Used to turn tweeting off, usually used for testing purposes",
                    action="store_true")
parser.add_argument("--limit", help="Specify how many items you want to tweet. If the limit is one then it checks your last update and if it has changed then it will tweet", default=10, type=check_number)

args = parser.parse_args()

artist = args.artists
track = args.tracks
album = args.albums

include_twitter_handles = args.at
tweet_args = args.tweet
limit = args.limit

if tweet_args:
    tweet = False
    print('Tweeting has been disabled', flush=True)
if include_twitter_handles:
    print('Artists names will be replaced with their twitter handle', flush=True)
    if include_twitter_handles == "add":
        # Add to the database
        add_to_database = True

if artist != None:
    if artist == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('artist', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('artist', artist, limit)

if track != None:
    if track == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('track', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('track', track, limit)

if album != None:
    if album == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('album', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('album', album, limit)
