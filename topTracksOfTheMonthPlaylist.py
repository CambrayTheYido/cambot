#!/usr/bin/env python
import datetime
import spotipy
from twython import Twython
import spotipy.util as util
import config
import twitter_handles as t

# Spotify API
scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret


# Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

#Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

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

playlist_name = "Top tracks of {} {}".format(month, now.year)

if token:
    sp = spotipy.Spotify(auth=token)

    # Create a new playlist
    playlist = sp.user_playlist_create(user=spotify_username, name=playlist_name, public=True)
    playlist_id = playlist.get('uri')


    # Get top 50 tracks from past month
    topTracks = sp.current_user_top_tracks(time_range='short_term', limit=50)

    list_of_tracks_to_add = []
    some_artists = []

    # Iterate through the tracks to get the relevant information
    for track in topTracks['items']:

        # Store a list of artists to involve in the tweet
        artist = t.is_artist_in_dict(track['artists'][0].get('name'))
        if artist not in some_artists:
            some_artists.append(artist)

        list_of_tracks_to_add.append(track['uri'])

    sp.user_playlist_add_tracks(user=spotify_username, playlist_id=playlist_id, tracks=list_of_tracks_to_add)
else:
    print("Can't get token for", spotify_username)

playlist_link_url = playlist['external_urls']
playlist_link_url = playlist_link_url.get('spotify')
tweet_str = "Here's a spotify playlist of my most listened to songs in " + month + "\n" + playlist_link_url + "\n" + "This includes artists such as: "
for artist in some_artists:
    if len(tweet_str) + len(artist) <= 280:
        tweet_str+= artist + ", "
tweet_str = tweet_str[:-2] + "."
print(tweet_str)
api.update_status(status=tweet_str)
