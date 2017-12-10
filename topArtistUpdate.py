#!/usr/bin/env python
import sys
import pylast
import spotipy
import spotipy.util as util
from twython import Twython
import config
import os
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

# Get my top artist
topArtist = user.get_top_artists(period='7day', limit='1')
# Get the artist
for x in topArtist:
    search = x[0]

if len(sys.argv) > 1:
    search_str = sys.argv[1]
else:
    search_str = search

sp = spotipy.Spotify(auth=token)
result = sp.search(search, type='artist', limit='1')
things = result['artists']['items']
for artist in things:
    url = artist['external_urls']
    # Extract the URL from the dictionary
    url = url.get('spotify')

artist_name = twitter_handles.is_artist_in_dict(str(search_str))
# Check if the URL has already been tweeted lately, if not then tweet new link
path = os.getcwd()
file_name = "topArtistURL.txt"
file_name_and_path = path + "/" + file_name
file = open(file_name_and_path, "r")
for line in file:
    if line != url:
        file = open(file_name_and_path, "w")
        file.write(url)
        file.close
        tweetStr = "#TopArtistUpdate \n" + artist_name + "\n" + str(url)
        api.update_status(status=tweetStr)
