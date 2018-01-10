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

list_of_tweets = api.get_user_timeline(screen_name="BotCambray")
last_tweet = list_of_tweets[0].get('id_str')

topArtists = user.get_top_artists(period='12month', limit=20)
count = 1
reverse_this_list = []

for artist in topArtists:
    artist_name = artist[0]
    plays = artist[1]

    result = sp.search(artist_name, limit='1', type='artist')
    things = result['artists']['items']
    for get_url in things:
        url = get_url['external_urls']
        url = url.get('spotify')

    twitter_at_artist = twitter_handles.is_artist_in_dict(artist_name)


    tweet = str(count) + ". " + twitter_at_artist + " (" + plays + " plays)\n" + url
    reverse_this_list.append(tweet)

    count+=1

count_to_begin_thread = 0
reverse_this_list.reverse()
for artist_tweet in reverse_this_list:
    if count_to_begin_thread > 0:
        list_of_tweets = api.get_user_timeline(screen_name="BotCambray")
        tweet_to_reply_to = list_of_tweets[0].get('id')
        api.update_status(status="#MyTopArtistsOfTheYear\n" + artist_tweet, in_reply_to_status_id=tweet_to_reply_to)
    else:
        api.update_status(status="#MyTopArtistsOfTheYear\n" + artist_tweet)
    count_to_begin_thread+=1

    print(artist_tweet)
    time.sleep(30)