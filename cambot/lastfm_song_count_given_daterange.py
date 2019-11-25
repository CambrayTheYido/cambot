#!/usr/bin/env python
from datetime import datetime,timedelta
import time
import operator
import pylast
import sys
from twython import Twython
import argparse
import cambot.config as config

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

TWEET = True

def get_count_of_songs_played(time_range):
    # Decide if we need to tweet about today or over a set of days
    if time_range == 1:
        tweet_date_range = ""
    else:
        tweet_date_range = "over the last {} days".format(time_range)

    # We need the start of the current day up until the time the script is run.
    date_from = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # If the script is running anything other than the last day, minus those days
    if time_range != 1:
        date_from = date_from - timedelta(days=time_range)

    # LastFM api uses the epoch timing so we convert it to unix time
    unix_d = time.mktime(date_from.timetuple())

    # list_of_tracks returns the list of tracks played from the beginning of the day the script is run to the exact time the script is run

    # List of genres
    genre_list = []

    list_of_tracks = user.get_recent_tracks(None, False, time_from=unix_d, time_to=time.time())
    for extract_track_details in list_of_tracks:
        artist = extract_track_details[0]
        artist = str(artist).split("-")[0].strip(" ")
        try:
            artist_genre = network.get_artist(artist_name=artist).get_top_tags()
            for genre in artist_genre:
                genre_to_add = genre[0]
                genre_list.append(str(genre_to_add))
        except:
            continue

    count = len(list_of_tracks)
    if count > 0:
        # How many songs have been played
        count = len(list_of_tracks) + 1  # starts at 0, so add 1, because... yes
        genre_count = {}
        disregard_tag = ["seen live", "live_seen", "nyc", "Loops3N", "1Live Fiehe", "Nottingham", "Hospital Records Label", "Dnb Stuff", "The Weeknd", "Swag", "jihad", "eye q", "Tolistento"]
        for genre in genre_list:
            if genre not in genre_count:
                genre_count[genre] = 0
            genre_count[genre] += 1
        sorted_genre = sorted(genre_count.items(), key=operator.itemgetter(1), reverse=True)
        sorted_genre = dict(sorted_genre)
        popular_tags = "The most popular tags of the songs I listened to {} were: ".format(tweet_date_range)
        counter = 0
        for key in sorted_genre:
            # Depending on number of songs listened to, number of tags to stop at increases with songs listened to.
            if counter == int(count/8 + 1) or len(popular_tags) >= 200:
                break
            else:
                if str(key).lower() in [x.lower() for x in disregard_tag]:
                    continue
                else:
                    chars_to_remove = [' ', '-']
                    sc = set(chars_to_remove)
                    key = key.title()
                    popular_tags += "#" + ''.join([c for c in key if c not in sc]) + " "
                    counter += 1

    if count == 1:
        song = " song "
    else:
        song = " songs "

    tweetStr = "I listened to {}{}{}.\n{}".format(count, song, tweet_date_range, popular_tags)
    print(tweetStr)
    if TWEET:
        api.update_status(status=tweetStr)

parser = argparse.ArgumentParser()
parser.add_argument("--range",
                    help="Tweets the amount of songs played over the range specified. You input a number and that number is equal to how many days you want to get the songs you played over.",
                    default=1, type=int)
parser.add_argument("-t", "--tweet",
                    help="If this has been entered, then the script will NOT tweet to the account provided.",
                    action="store_true")
args = parser.parse_args()

if args.tweet:
    TWEET = False
    print("Tweeting has been disabled", flush=True)
if args.range:
    get_count_of_songs_played(args.range)