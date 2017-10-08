#!/usr/bin/env python
import sys
from twython import Twython
import pylast
import spotipy
import spotipy.util as util
import config

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username
last_fm_password = config.lastfm_password_hash

network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)

# Spotify APIscope = 'user-library-read'
userTop = config.spotfiy_user_top
last_fm_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

token = util.prompt_for_user_token(last_fm_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=userTop)

topTrack = user.get_top_tracks(period='7day', limit='1')

for x in topTrack:
    search = x[0]

if len(sys.argv) > 1:
    search_str = sys.argv[1]
else:
    search_str = search

sp = spotipy.Spotify(auth=token)
result = sp.search(search, limit='1')
things = result['tracks']['items']
for tracko in things:
    url = tracko['external_urls']
    url = url.get('spotify')

# Check if the URL has already been tweeted lately, if not then tweet new link
files = open("topTrackURL.txt", "r")
for line in files:
    if line != url:
        file = open("topTrackURL.txt", "w")
        file.write(url)
        file.close
        tweetStr = "#TopTrackUpdate \n" + str(search) + "\n" + str(url)
        api.update_status(status=tweetStr)
