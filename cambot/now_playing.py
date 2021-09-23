#!/usr/bin/env python
import time

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

playingTrack = None
while 1 < 2:  # DO YOU GET IT??
    nowPlaying = user.get_now_playing()
    if nowPlaying == playingTrack or nowPlaying is None:
        time.sleep(15)
    else:
        playingTrack = user.get_now_playing()
        api.update_status(status="#NowPlaying " + str(playingTrack))
        print(playingTrack)
        time.sleep(15)

# This does not get used as it turns out this is quite annoying