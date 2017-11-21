#!/usr/bin/env python
import pylast
from twython import Twython

import config
import twitter_handles

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


top_artist_and_plays_string_to_tweet = "#TopArtistsOfTheWeek \n"
plays = " plays \n"
count = 1
topArtist = user.get_top_artists(period='7day')
for x in topArtist:
    artist_name = str(x[0])
    artist_name = twitter_handles.is_artist_in_dict(artist_name)

    playcount = str(x[1])

    add_to_tweet = str(count) + ". " + artist_name + " - " + playcount + plays

    if len(top_artist_and_plays_string_to_tweet) + len(add_to_tweet) <= 280:
        top_artist_and_plays_string_to_tweet += add_to_tweet
        count+=1

print(top_artist_and_plays_string_to_tweet)

api.update_status(status=top_artist_and_plays_string_to_tweet)