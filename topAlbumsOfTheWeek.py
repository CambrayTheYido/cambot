#!/usr/bin/env python
import pylast
from twython import Twython
import twitter_handles
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

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

top = "#TopAlbumsOfTheWeek\n"

topalbum = user.get_top_albums(period='7day')
count = 0
for x in topalbum:
    album_name = str(x[0])
    album_name = twitter_handles.is_artist_in_dict(album_name)
    count += 1
    add_to_tweet = str(count) + ". " + album_name + "\n"
    if len(top) + len(add_to_tweet) <= 280:
        top += add_to_tweet
    else:
        break
print(top)
api.update_status(status=top)
