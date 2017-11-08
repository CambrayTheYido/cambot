#!/usr/bin/env python
import spotipy
import spotipy.util as util
from twython import Twython

import config

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify API
userTop = config.spotfiy_user_top
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=userTop)

tweetstr = "My #TopArtists over the last month!\n"
if token:
    sp = spotipy.Spotify(auth=token)
    topArtists = sp.current_user_top_artists(time_range='short_term')
    for artist in topArtists['items']:
        artistStr = artist['name']
        if len(tweetstr) + len(str(artistStr)) <= 280:
            tweetstr += artist['name'] + "\n"
        else:
            break
else:
    print("Can't get token for", spotify_username)

api.update_status(status=tweetstr)
