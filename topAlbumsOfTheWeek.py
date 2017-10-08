#!/usr/bin/env python
import pylast
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

top = "#TopAlbumsOfTheWeek\n"

topalbum = user.get_top_albums(period='7day')
count = 0
for x in topalbum:
    album_name = str(x[0])
    count += 1
    if len(top) + len(album_name) <= 135:
        top += str(count) + " - " + album_name + "\n"
    else:
        break

api.update_status(status=top)
