#!/usr/bin/env python
from twython import Twython
import pylast
import spotipy
import spotipy.util as util
import config
import twitter_handles
import os
import argparse
import time

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

sp = spotipy.Spotify(auth=token)

NO_UPDATE_NEEDED = "Information up to date and already tweeted."
TWEET_STATUS_UPDATE = True


def top_track_update(period):
    # Get the top track from the specified time frame
    topTrack = user.get_top_tracks(period=period, limit='1')

    for x in topTrack:
        search_str = str(x[0])

    search = "\'" + str(search_str) + "\'"
    url = ""
    try:
        result = sp.search(search, limit='1', type='track')
        things = result['tracks']['items']
        for track in things:
            url = track['external_urls']
            url = url.get('spotify')
    except:
        print("could not get a spotify result", flush=True)

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topTrackUpdate7day.txt"
        topTrackTimeFrame = "#TopTrackOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topTrackUpdate1month.txt"
        topTrackTimeFrame = "New #TopTrackUpdate of the month"
    elif period == "3month":
        file_name = "topTrackUpdate3month.txt"
        topTrackTimeFrame = "New #TopTrackUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topTrackUpdate6month.txt"
        topTrackTimeFrame = "New #TopTrackUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topTrackUpdate12month.txt"
        topTrackTimeFrame = "New #TopTrackUpdate of the last year"
    elif period == "overall":
        file_name = "topTrackUpdateOverall.txt"
        topTrackTimeFrame = "New #TopTrackUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search_str:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search_str)
        file.close()
        tweetStr = topTrackTimeFrame + "\n\n" + search_str + "\n" + str(url)
        print(tweetStr, flush=True)
        try:
            if TWEET_STATUS_UPDATE:
                api.update_status(status=tweetStr)
                # Just to reduce the spam load a little.
                time.sleep(5)
        except:
            print("Could not tweet latest track update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()


def top_album_update(period):
    # Get my top album
    topAlbum = user.get_top_albums(period=period, limit='1')
    # Get the album name
    for x in topAlbum:
        search = str(x[0])

    url = ""
    result = sp.search(search, type='album', limit='1')
    things = result['albums']['items']
    for album in things:
        url = album['external_urls']
        # Extract the URL from the dictionary
        url = url.get('spotify')

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topAlbumUpdate7day.txt"
        topAlbumTimeFrame = "#TopAlbumOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topAlbumUpdate1month.txt"
        topAlbumTimeFrame = "New #TopAlbumUpdate of the month"
    elif period == "3month":
        file_name = "topAlbumUpdate3month.txt"
        topAlbumTimeFrame = "New #TopAlbumUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topAlbumUpdate6month.txt"
        topAlbumTimeFrame = "New #TopAlbumUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topAlbumUpdate12month.txt"
        topAlbumTimeFrame = "New #TopAlbumUpdate of the last year"
    elif period == "overall":
        file_name = "topAlbumUpdateOverall.txt"
        topAlbumTimeFrame = "New #TopAlbumUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search)
        file.close()
        tweetStr = topAlbumTimeFrame + "\n\n" + search + "\n" + str(url)
        print(tweetStr, flush=True)
        try:
            if TWEET_STATUS_UPDATE:
                api.update_status(status=tweetStr)
                # Just to reduce the spam load a little.
                time.sleep(5)
        except:
            print("Could not tweet latest track update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()


def top_artist_update(period):
    # Get my top artist
    topArtist = user.get_top_artists(period=period, limit='1')
    # Get the artist
    for x in topArtist:
        search_str = str(x[0])

    result = sp.search(search_str, type='artist', limit='1')
    things = result['artists']['items']
    url = ""
    for artist in things:
        url = artist['external_urls']
        # Extract the URL from the dictionary
        url = url.get('spotify')

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topArtistUpdate7day.txt"
        topArtistTimeFrame = "#TopArtistOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topArtistUpdate1month.txt"
        topArtistTimeFrame = "New #TopArtistUpdate of the month"
    elif period == "3month":
        file_name = "topArtistUpdate3month.txt"
        topArtistTimeFrame = "New #TopArtistUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topArtistUpdate6month.txt"
        topArtistTimeFrame = "New #TopArtistUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topArtistUpdate12month.txt"
        topArtistTimeFrame = "New #TopArtistUpdate of the last year"
    elif period == "overall":
        file_name = "topArtistUpdateOverall.txt"
        topArtistTimeFrame = "New #TopArtistUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search_str:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search_str)
        file.close()
        tweetStr = topArtistTimeFrame + "\n\n" + search_str + "\n" + str(url)
        print(tweetStr, flush=True)
        try:
            if TWEET_STATUS_UPDATE:
                api.update_status(status=tweetStr)
                # Just to reduce the spam load a little.
                time.sleep(5)
        except:
            print("Could not tweet latest Artist update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()


choices = ["7day", "1month", "3month", "6month", "12month", "overall", "all"]

parser = argparse.ArgumentParser()
parser.add_argument("--track",
                    help="Tweets the top track from the specified time frame, if it has not already been tweeted recently",
                    default="7day", choices=choices)
parser.add_argument("--album",
                    help="Tweets the top album from the specified time frame, if it has not already been tweeted recently",
                    default="7day", choices=choices)
parser.add_argument("--artist",
                    help="Tweets the top artist from the specified time frame, if it has not already been tweeted recently",
                    default="7day", choices=choices)
parser.add_argument("-t", "--tweet",
                    help="If this has been entered, then the script will NOT tweet to the account provided.",
                    action="store_true")
args = parser.parse_args()

if args.tweet:
    TWEET_STATUS_UPDATE = False
    print("Tweeting has been disabled", flush=True)
if (args.track):
    if args.track == "all":
        for period in choices:
            if period == "all":
                break
            top_track_update(period)

    else:
        top_track_update(args.track)

if (args.artist):
    if args.artist == "all":
        for period in choices:
            if period == "all":
                break
            top_artist_update(period)

    else:
        top_artist_update(args.artist)

if (args.album):
    if args.album == "all":
        for period in choices:
            if period == "all":
                break
            top_album_update(period)

    else:
        top_album_update(args.album)
