#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import pymongo
import time
import logging
import config
import pylast
from twython import Twython
import spotipy
from spotipy.oauth2 import SpotifyOAuth

#TODO: Update this files name as its no longer just a holder for twitter handles when it was first introduced back in 2017 ore whatever!!

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]

logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# Spotify Token
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=config.spotify_scope, client_secret=config.spotify_client_secret,
                                               client_id=config.spotify_client_id,
                                               redirect_uri="http://localhost:8888/callback"))

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

def search_spotify(sp_instance, search_string, type):
    searchies = search_string.replace(" -", "")
    if type == 'artist':
        result = sp_instance.search(searchies, limit='1', type=type)
        result = result['artists']['items']
    elif type == 'track':
        # artist_track_split = search_string.split("-", maxsplit=1)
        # TODO: Figure out a way to enable this advanced searching. Issues: artist names with '-' in the name, not filtering radio edit / 'mixed' songs
        # track_search = "artist:'{}' track:'{}' -radioedit".format(str(artist_track_split[0]).strip(), str(artist_track_split[1]).strip())
        # print("spotify track search: {}".format(track_search), flush=True)
        result = sp_instance.search(searchies, limit='1', type=type)
        result = result['tracks']['items']
    elif type == 'album':
        result = sp_instance.search(searchies, limit='1', type=type)
        result = result['albums']['items']
    url = ''
    for item in result:
        url = item['external_urls']
        url = url.get('spotify')
    if url == '':
        logging.info('No results found in spotify search for {}'.format(search_string))
        return
    return url


def check_or_add_artist_names_to_database(artist_name, add_to_database):
    mydb = myclient["artist_names"]
    mycol = mydb["names_and_handles"]

    if mycol.find_one({"name": artist_name.lower()}) != None:
        return mycol.find_one({"name": artist_name.lower()})["handle"]
    else:
        # Check if we are adding to the database, if not just return artist
        if not add_to_database:
            return artist_name
        # The artist was not found, therefore add it to the database.
        logging.info(
            "Please enter the twitter handle for the following artist: {}. If they do not have a handle, enter 'no'".format(
                artist_name))
        handle = input()
        time.sleep(0.5)

        # Clarity checking to avoid accidental inserts
        if len(handle) == 0:
            logging.warning("You entered nothing (by mistake?).")
            check_or_add_artist_names_to_database(artist_name, add_to_database)

        if handle == "no":
            # Do not insert into db
            logging.info("Skipping artist. Not inserting into DB")
            return artist_name
        else:
            add = {"name": artist_name.lower(), "handle": handle}
            x = mycol.insert_one(add)
            logging.info("Succesfully added '{}' to the database".format(artist_name))
            # Now return the handle
            return handle

    # insert = [
    #             {"name": "yotto", "handle": "@yottomusic"},
    #              {"name": "deadmau5", "handle": "@deadmau5"},
    #              {"name": "eric prydz", "handle": "@ericprydz"},
    #              {"name": "dusky", "handle": "@duskymusic"},
    #              {"name": "maduk", "handle": "@MadukDnB"},
    #              {"name": "no mana", "handle": "@ihavenomanas"},
    #              {"name": "pryda", "handle": "@ericprydz (Pryda)"},
    #              {"name": "cirez d", "handle": "@ericprydz (Cirez D)"},
    #              {"name": "tonja holma" , "handle": "@ericprydz (Tonja Holma)"},
    #              {"name": "miike snow", "handle": "@miikesnow"},
    #              {"name": "london grammar", "handle": "@londongrammar"},
    #              {"name": "jme", "handle": "@JmeBBK"},
    #              {"name": "disclosure", "handle": "@disclosure"},
    #              {"name": "chase & status", "handle": "@chaseandstatus"},
    #              {"name": "kendrick lamar", "handle": "@kendricklamar"},
    #              {"name": "madeon", "handle": "@madeon"},
    #              {"name": "sub focus", "handle": "@subfocus"},
    #              {"name": "matt lange", "handle": "@MattLange"},
    #              {"name": "dimension" , "handle": "@dimension_uk"},
    #              {"name": "attlas" , "handle": "@attlas"},
    #              {"name": "draft" , "handle": "@DraftUK"},
    #              {"name": "i_o" , "handle": "@i_oofficial"},
    #              {"name": "grabbitz" , "handle": "@grabbitz"},
    #              {"name": "kölsch" , "handle": "@kolschofficial"},
    #              {"name": "HEYz" , "handle": "@heyzmsc"},
    #              {"name": "max cooper" , "handle": "@maxcoopermax"},
    #              {"name": "layton giordani" , "handle": "@LaytonGiordani"},
    #              {"name": "ocula" , "handle": "@OCULAmusic"}
    #   x = mycol.insert_many(insert)
