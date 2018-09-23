#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import pymongo
import time


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]


twitter_handles = {"yotto": "@yottomusic",
                   "deadmau5": "@deadmau5",
                   "eric prydz": "@ericprydz",
                   "dusky": "@duskymusic",
                   "maduk": "@MadukDnB",
                   "no mana": "@ihavenomanas",
                   "pryda": "@ericprydz (Pryda)",
                   "cirez d": "@ericprydz (Cirez D)",
                   "tonja holma" : "@ericprydz (Tonja Holma)",
                   "miike snow": "@miikesnow",
                   "london grammar": "@londongrammar",
                   "jme": "@JmeBBK",
                   "disclosure": "@disclosure",
                   "chase & status": "@chaseandstatus",
                   "kendrick lamar": "@kendricklamar",
                   "madeon": "@madeon",
                   "sub focus": "@subfocus",
                   "matt lange": "@MattLange",
                   "dimension" : "@dimension_uk",
                   "attlas" : "@attlas",
                   "draft" : "@DraftUK",
                   "i_o" : "@i_oofficial",
                   "grabbitz" : "@grabbitz",
                   "kölsch" : "@kolschofficial",
                   "HEYz" : "@heyzmsc",
                   "max cooper" : "@maxcoopermax",
                   "layton giordani" : "@LaytonGiordani",
                   "ocula" : "@OCULAmusic"
                   }


def is_artist_in_dict(artist_name):
    artist_name = str(artist_name)
    for key, value in twitter_handles.items():
        if artist_name.lower() == key.lower() or key.lower() in artist_name.lower():
            artist_name = artist_name.lower().replace(key.lower(), value)
            break
    return ' '.join([word.capitalize() for word in artist_name.split(' ')])

def search_spotify(sp_instance, search_string, type):
    result = sp_instance.search(search_string, limit='1', type=type)
    if type == 'artist':
        result = result['artists']['items']
    elif type == 'track':
        result = result['tracks']['items']
    elif type == 'album':
        result = result['albums']['items']
    url = ''
    for item in result:
        url = item['external_urls']
        url = url.get('spotify')
    if url == '':
        print('No results found in spotify search for {}'.format(search_string), flush=True)
    return url

def check_or_add_artist_names_to_database(artist_name, add_to_database):
  dblist = myclient.list_database_names()
  mydb = myclient["artist_names"]
  mycol = mydb["names_and_handles"]

  if mycol.find_one({"name" : artist_name.lower()}) != None:
    return mycol.find_one({"name" : artist_name.lower()})["handle"]
  else:
    # Check if we are adding to the database, if not just return artist
    if not add_to_database:
      return artist_name
    # The artist was not found, therefore add it to the database. 
    print("Please enter the twitter handle for the following artist: {}. If they do not have a handle, enter 'no'".format(artist_name))
    handle = input()
    time.sleep(0.5)

  
    # Clarity checking to avoid accidental inserts
    if len(handle) == 0:
      print("You entered nothing (by mistake?) You have a second chance.")
      handle = input()


    if handle == "no":
      # Do not insert into db
      print("Skipping artist. Not inserting into DB")
      return artist_name
    else:
      add = { "name" : artist_name.lower(), "handle": handle}
      x = mycol.insert_one(add)
      print("Succesfully added '{}' to the database".format(artist_name))
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
