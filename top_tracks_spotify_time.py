#!/usr/bin/env python
import spotipy
import spotipy.util as util
from twython import Twython
import config
import argparse
import twitter_handles as t

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


def get_top_tracks(time_range):

    if time_range == "short_term":
        term = "month"
    elif time_range == "medium_term":
        term = "6 months"
    elif time_range == "long_term":
        term = "few years"

    tweet_str = "My #TopTracks over the past {} \n".format(term)

    if token:
        sp = spotipy.Spotify(auth=token)
        topTracks = sp.current_user_top_tracks(time_range=time_range)
        for track in topTracks['items']:
            # Get name of track
            song_name = track['name']
            # Get artist name
            list_of_artists = track['artists']
            list_of_artists = list_of_artists[0]
            artist = list_of_artists['name']

            artist = t.is_artist_in_dict(artist)

            if len(tweet_str) + len(song_name) + len(artist) <= 278:
                tweet_str += str(artist) + " - " + track['name'] + "\n"
            else:
                break

    else:
        print("Can't get token for", spotify_username)

    print(tweet_str)
    api.update_status(status=tweet_str)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--short", help="Tweets top tracks from the past month", action="store_true")
parser.add_argument("-m","--medium", help="Tweets top tracks from the past 6 months", action="store_true")
parser.add_argument("-l","--long", help="Tweets top tracks from the past few years", action="store_true")
args = parser.parse_args()

if(args.short):
    get_top_tracks("short_term")
if(args.medium):
    get_top_tracks("medium_term")
if(args.long):
    get_top_tracks("long_term")