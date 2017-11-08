#!/usr/bin/env python

import pylast
import spotipy
import spotipy.util as util
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

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)

# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

# Get my top album
topAlbum = user.get_top_albums(period='7day', limit='1')
# Get the album name
for x in topAlbum:
    search = x[0]

sp = spotipy.Spotify(auth=token)
result = sp.search(search, type='album', limit='1')
things = result['albums']['items']
for album in things:
    url = album['external_urls']
    # Extract the URL from the dictionary
    url = url.get('spotify')

# Check if the URL has already been tweeted lately, if not then tweet new link
filename = "topAlbumURL.txt"
file = open(filename, "r")
for line in file:
    if line != url:
        file = open(filename, "w")
        file.write(url)
        file.close
        tweetStr = "#TopAlbumUpdate \n" + str(search) + "\n" + str(url)
        api.update_status(status=tweetStr)
