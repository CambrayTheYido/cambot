#!/usr/bin/env python
import spotipy
import spotipy.util as util
from twython import Twython
import config
import twitter_handles

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

tweet_str = "My #TopTracks over the years! \n"
count = 1

if token:
    sp = spotipy.Spotify(auth=token)
    topTracks = sp.current_user_top_tracks(time_range='long_term')
    for track in topTracks['items']:
        # Get name of track
        song_name = track['name']
        # Get artist name
        list_of_artists = track['artists']
        list_of_artists = list_of_artists[0]
        artist_name = list_of_artists['name']
        artist_name = twitter_handles.is_artist_in_dict(artist_name)

        string_to_add = str(count) + ". " + str(artist_name) + " - " + str(song_name) + "\n"

        if len(tweet_str) + len(song_name) + len(artist_name) <= 280:
            tweet_str += string_to_add
            count+=1
        else:
            break

else:
    print("Can't get token for", spotify_username)
print(tweet_str)
api.update_status(status=tweet_str)
