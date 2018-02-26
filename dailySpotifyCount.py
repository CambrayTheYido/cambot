#!/usr/bin/env python
import datetime
import time
import operator
import pylast
import sys
from twython import Twython

import config

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username
last_fm_password = config.lastfm_password_hash

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)

# We need the start of the current day up until the time the script is run.
d = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# LastFM api uses the epoch timing so we convert it to unix time
unix_d = time.mktime(d.timetuple())

# list_of_tracks returns the list of tracks played from the beginning of the day the script is run to the exact time the
# script is run

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
# How many spotify songs have been played
count = len(list_of_tracks) + 1 # starts at 0, so add 1, because... yes

if count > 0:
    genre_count = {}
    disregard_tag = ["seen live", "live_seen", "nyc", "Loops3N", "1Live Fiehe", "Nottingham", "Hospital Records Label", "Dnb Stuff", "The Weeknd", "Swag", "jihad", "eye q", "Tolistento"]
    for genre in genre_list:
        if genre not in genre_count:
            genre_count[genre] = 0
        genre_count[genre] += 1
    sorted_genre = sorted(genre_count.items(), key=operator.itemgetter(1), reverse=True)
    sorted_genre = dict(sorted_genre)
    popular_tags = "The most popular tags of the songs I listened to today were: "
    counter = 0
    for key in sorted_genre:
        # Depending on number of songs listened to, number of tags to stop at increases with songs listened to.
        if counter == int(count/8 + 1):
            # Replace last comma with a full stop
            popular_tags = popular_tags[:-2]
            popular_tags += "."
            break
        else:
            if str(key).lower() in [x.lower() for x in disregard_tag]:
                continue
            else:
                popular_tags += str(key).title() + ", "
                counter += 1

if count == 1:
    song = " song "
else:
    song = " songs "

tweetStr = "I played " + str(count) + song + "on spotify today.\n" + popular_tags
print(tweetStr)
api.update_status(status=tweetStr)
