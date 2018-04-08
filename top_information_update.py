#!/usr/bin/env python
import sys
from twython import Twython
import pylast
import spotipy
import spotipy.util as util
import config
import twitter_handles
import os
import argparse

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

NO_UPDATE_NEEDED = "Information up to date and already tweeted."

def top_track_update():
    # Get the top track from the last 7 days
    topTrack = user.get_top_tracks(period='7day', limit='1')

    for x in topTrack:
        search = x[0]

    if len(sys.argv) > 1:
        search_str = sys.argv[1]
    else:
        search_str = str(search)

    sp = spotipy.Spotify(auth=token)
    search = "\'" + str(search) + "\'"
    result = sp.search(search, limit='1', type='track')
    things = result['tracks']['items']
    url = ""
    for track in things:
        url = track['external_urls']
        url = url.get('spotify')

        artist_name = str(track['artists'][0].get('name'))
        artist_name_with_at = twitter_handles.is_artist_in_dict(artist_name)

        if artist_name.lower() in search_str.lower():
            search_str = search_str.replace(artist_name.lower(), artist_name_with_at, 1)

    # Check if the URL has already been tweeted lately, if not then tweet new link
    path = os.getcwd()
    file_name = "topTrackURL.txt"
    file_name_and_path = path + "/" + file_name
    files = open(file_name_and_path, "r+")
    if os.stat(file_name).st_size == 0:
        files.write("empty")
    for line in files:
        if line != url:
            file = open(file_name_and_path, "w")
            file.write(url)
            file.close
            tweetStr = "#TopTrackUpdate \n" + search_str + "\n" + str(url)
            print(tweetStr)
            api.update_status(status=tweetStr)
        else:
            print(NO_UPDATE_NEEDED)



def top_album_update():
    # Get my top album
    topAlbum = user.get_top_albums(period='7day', limit='1')
    # Get the album name
    for x in topAlbum:
        search = str(x[0])

    url = ""
    sp = spotipy.Spotify(auth=token)
    result = sp.search(search, type='album', limit='1')
    things = result['albums']['items']
    for album in things:
        url = album['external_urls']
        # Extract the URL from the dictionary
        url = url.get('spotify')

    # Check if the URL has already been tweeted lately, if not then tweet new link
    artist_name = twitter_handles.is_artist_in_dict(search.split('-')[0].strip())
    string_to_tweet = search.replace(search.split('-')[0], artist_name + " ")

    path = os.getcwd()
    file_name = "topAlbumURL.txt"
    file_name_and_path = path + "/" + file_name
    file = open(file_name_and_path, "r+")
    if os.stat(file_name).st_size == 0:
        file.write("empty")
    for line in file:
        if line != url:
            file = open(file_name_and_path, "w")
            file.write(url)
            file.close
            tweetStr = "#TopAlbumUpdate \n" + string_to_tweet + "\n" + str(url)
            print(tweetStr)
            api.update_status(status=tweetStr)
        else:
            print(NO_UPDATE_NEEDED)



def top_artist_update():
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
    file = open(file_name_and_path, "r+")
    if os.stat(file_name).st_size == 0:
        file.write("empty")
    for line in file:
        if line != url:
            file = open(file_name_and_path, "w")
            file.write(url)
            file.close
            tweetStr = "#TopArtistUpdate \n" + artist_name + "\n" + str(url)
            print(tweetStr)
            api.update_status(status=tweetStr)
        else:
            print(NO_UPDATE_NEEDED)

if sys.argv.__contains__("track"):
    top_track_update()
elif sys.argv.__contains__("album"):
    top_album_update()
elif sys.argv.__contains__("artist"):
    top_artist_update()