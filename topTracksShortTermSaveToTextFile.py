#!/usr/bin/env python
import datetime
import spotipy

import spotipy.util as util
import config

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

now = datetime.datetime.now()
month = now.month
if (month == 1):
    month = "January"
elif (month == 2):
    month = "February"
elif (month == 3):
    month = "March"
elif (month == 4):
    month = "April"
elif (month == 5):
    month = "May"
elif (month == 6):
    month = "June"
elif (month == 7):
    month = "July"
elif (month == 8):
    month = "August"
elif (month == 9):
    month = "September"
elif (month == 10):
    month = "October"
elif (month == 11):
    month = "November"
elif (month == 12):
    month = "December"

if token:
    sp = spotipy.Spotify(auth=token)
    topTracks = sp.current_user_top_tracks(time_range='short_term')
    for track in topTracks['items']:
        # Get name of track
        song_name = track['name']
        # Get artist name
        list_of_artists = track['artists']
        list_of_artists = list_of_artists[0]
        artist = list_of_artists['name']

        line_to_write = str(artist) + " - " + str(song_name) + "\n"

        file = open("Top tracks of " + str(month) + ".txt", "a")
        file.write(line_to_write)
        print(line_to_write)

else:
    print("Can't get token for", spotify_username)
