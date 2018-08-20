#!/usr/bin/env python
import pylast
from twython import Twython
import argparse
import config
import spotipy
import spotipy.util as util
import twitter_handles
import datetime
from dateutil.relativedelta import *

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

#Spotify Token
token = util.prompt_for_user_token(username=spotify_username, client_id=client_id, client_secret=client_secret,
                                   redirect_uri="http://localhost:8090", scope=scope)
sp = spotipy.Spotify(auth=token)

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

age_of_account_in_years_months = datetime.datetime.utcfromtimestamp(int(user.get_registered())).strftime('%Y-%m-%d')

age_of_account_in_years_months = datetime.date(int(age_of_account_in_years_months.split('-')[0]), int(age_of_account_in_years_months.split('-')[1]), int(age_of_account_in_years_months.split('-')[2]))

age_of_account_in_years_months = str(relativedelta(datetime.date.today(), age_of_account_in_years_months).years) + \
                                 ' years and ' + str(relativedelta(datetime.date.today(), age_of_account_in_years_months).months) \
                                 + ' months'

time_frames = {'7day': 'week',
               '1month': 'month',
              '3month': '3 months',
              '6month': '6 months',
              '12month': 'year',
               # leave overall blank and work out length using age of account
              'overall': age_of_account_in_years_months}

PLAYS = " plays\n"

def gather_relevant_information_to_request(type, time_frame, amount_of_tweets):
    if type == 'artist':
        # determine period to use
        top = user.get_top_artists(period=time_frame)
        beginning_of_tweet = "#TopArtists of the last {}".format([value for key, value in time_frames.items() if time_frame in key.lower()])
        add_to_tweet = get_top_artist_information(top, amount_of_tweets)
        tweet = beginning_of_tweet + add_to_tweet
    elif type == 'track':
        top = user.get_top_tracks(period=time_frame)


    elif type == 'album':
        top = user.get_top_albums(period=time_frame)

    api.update_status(status=tweet)

def search_spotify(search_string):
    result = sp.search(search_string, limit='1')
    result = result['tracks']['items']
    url = ''
    for item in result:
        url = item['external_urls']
        url = url.get('spotify')
    return url

def get_top_artist_information(list_of_artists, tweet_count):
    for x in list_of_artists:
        if count > tweet_count:
            break

        artist_name = str(x[0])
        artist_name = twitter_handles.is_artist_in_dict(artist_name)

        count = 1

        playcount = str(x[1])

        add_to_tweet = str(count) + ". " + artist_name + " - " + playcount + PLAYS + search_spotify(artist_name)
        api.update_status(status=add_to_tweet)

choices = ["7day", "1month", "3month", "6month", "12month", "overall"]

parser = argparse.ArgumentParser()
parser.add_argument("--tracks",
                    help="Tweets the top tracks from the specified time frame and chains the tweets in a thread",
                    default="7day", choices=choices)
parser.add_argument("--albums",
                    help="Tweets the top albums from the specified time frame and chains the tweets in a thread",
                    default="7day", choices=choices)
parser.add_argument("--artists",
                    help="Tweets the top artists from the specified time frame and chains the tweets in a thread",
                    default="7day", choices=choices)

args = parser.parse_args()

if args.artists:
    gather_relevant_information_to_request('artist', args.artists, 10)
