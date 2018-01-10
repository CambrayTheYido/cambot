import pylast
import sys
import argparse
from twython import Twython
import config
import twitter_handles
import spotipy
import spotipy.util as util
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

#Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)

sp = spotipy.Spotify(auth=token)

parser = argparse.ArgumentParser(description='A script that tweets your top songs, artists, albums. All from last.fm API')
parser.add_argument('--songs', type=int, help='Tweet your top songs from the past year')
parser.add_argument('--artists', type=int, help='Tweet your top artists from the past year')
parser.add_argument('--albums', type=int, help='Tweet your top albums from the past year')

args = parser.parse_args()

topTracksWeek = user.get_top_tracks(period='12month', limit=20)
count = 1
reverse_this_list = []
for track in topTracksWeek:
    track_and_artist = str(track[0])
    plays_of_track = str(track[1])

    result = sp.search(track_and_artist, limit='1')
    things = result['tracks']['items']
    for track in things:
        url = track['external_urls']
        url = url.get('spotify')

    twitter_at_artist_and_track = twitter_handles.is_artist_in_dict(track_and_artist)


    tweet = str(count) + ". " + twitter_at_artist_and_track + " (" + plays_of_track + " plays)\n" + url
    reverse_this_list.append(tweet)

    count+=1

list_of_tweets = api.get_user_timeline(screen_name="BotCambray")

api.update_status(status=, in_reply_to_status_id=)

# Reverse the list
reverse_this_list.reverse()
for song in reverse_this_list:
    #api.update_status(status="#MyTopTracksOfTheYear\n" + song)

    print(song)
    time.sleep(30)
