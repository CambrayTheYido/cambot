#!/usr/bin/env python
import spotipy
import spotipy.util as util
from twython import Twython
import config
import argparse
import utils as t

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


def determine_time_range(time_range):
    if time_range == "short_term":
        term = "month"
    elif time_range == "medium_term":
        term = "6 months"
    elif time_range == "long_term":
        term = "few years"
    return term


def get_top_artists(time_range):
    term = determine_time_range(time_range)

    tweet_str = "My #TopArtists over the past {} \n".format(term)

    if token:
        sp = spotipy.Spotify(auth=token)
        topArtists = sp.current_user_top_artists(time_range=time_range)
        for artist in topArtists['items']:
            artistStr = artist['name']
            if len(tweet_str) + len(str(artistStr)) <= 280:
                tweet_str += artistStr + "\n"
            else:
                break
    else:
        print("Can't get token for", spotify_username)

    print(tweet_str, flush=True)
    if TWEET_STATUS_UPDATE:
        api.update_status(status=tweet_str)


def get_top_tracks(time_range):
    term = determine_time_range(time_range)

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

            if include_artist_twitter_handle:
                artist = utils.is_artist_in_dict(artist)

            if len(tweet_str) + len(song_name) + len(artist) <= 278:
                tweet_str += str(artist) + " - " + track['name'] + "\n"
            else:
                break

    else:
        print("Can't get token for", spotify_username)

    print(tweet_str, flush=True)
    if TWEET_STATUS_UPDATE:
        api.update_status(status=tweet_str)


choices = ["track", "artist", "all"]
short_term = "short_term"
medium_term = "medium_term"
long_term = "long_term"
terms = [short_term, medium_term, long_term]

TWEET_STATUS_UPDATE = True

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--shortterm", help="Tweets top information from the past month", default="track",
                    choices=choices, dest="shortterm")
parser.add_argument("-m", "--mediumterm", help="Tweets top information from the past 6 months", default="track",
                    choices=choices, dest="mediumterm")
parser.add_argument("-l", "--longterm", help="Tweets top information from the past few years", default="track",
                    choices=choices)
parser.add_argument("-t", "--tweet",
                    help="If this has been entered, then the script will NOT tweet to the account provided.",
                    action="store_true")
parser.add_argument("-a", "--at",
                    help="Include this at runtime to replace mentions of artists names with their twitter handles (if they are stored)",
                    action="store_true")
args = parser.parse_args()

tweet = args.tweet
include_artist_twitter_handle = args.at
shortterm = args.shortterm
mediumterm = args.mediumterm
longterm = args.longterm

if tweet:
    TWEET_STATUS_UPDATE = False
    print("Tweeting has been disabled", flush=True)


if shortterm:
    if shortterm == "all":
        get_top_artists(short_term)
        get_top_tracks(short_term)
    else:
        for arguments in shortterm:
            if arguments == "track":
                get_top_tracks(short_term)
            if arguments == "artist":
                get_top_artists(short_term)

if mediumterm:
    if mediumterm == "all":
        get_top_tracks(medium_term)
        get_top_artists(medium_term)
    else:
        if arguments == "track":
            get_top_tracks(medium_term)
        elif arguments == "artist":
            get_top_artists(medium_term)

if longterm:
    if longterm == "all":
        get_top_tracks(long_term)
        get_top_artists(long_term)
    else:
        for arguments in longterm:
            if arguments == "track":
                get_top_tracks(long_term)
            if arguments == "artist":
                get_top_artists(long_term)
