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
from time import sleep

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

scope = config.spotify_scope
spotify_username = config.spotify_username
client_id = config.spotify_client_id
client_secret = config.spotfiy_client_secret

# Spotify Token
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

age_of_account_in_years_months = datetime.date(int(age_of_account_in_years_months.split('-')[0]),
                                               int(age_of_account_in_years_months.split('-')[1]),
                                               int(age_of_account_in_years_months.split('-')[2]))

age_of_account_in_years_months = str(relativedelta(datetime.date.today(), age_of_account_in_years_months).years) + \
                                 ' years and ' + str(
    relativedelta(datetime.date.today(), age_of_account_in_years_months).months) \
                                 + ' months'

time_frames = {'7day': 'week',
               '1month': 'month',
               '3month': '3 months',
               '6month': '6 months',
               '12month': 'year',
               # leave overall blank and work out length using age of account
               'overall': age_of_account_in_years_months}

PLAYS = " plays\n"

tweet = True


def get_latest_tweet():
    tweet = api.get_user_timeline(screen_name="BotCambray")
    return tweet[0].get('id')


def gather_relevant_information_to_request(type, time_frame):
    if type == 'artist':
        # determine period to use
        top = user.get_top_artists(period=time_frame)
        first_tweet = "My most listened to #Artists of the last {}".format(
            [value for key, value in time_frames.items() if time_frame in key.lower()][0])
        print(first_tweet, flush=True)

        # Tweet the first tweet to get the ball rolling, grab the ID of the tweet while we're at it
        if tweet:
            api.update_status(status=first_tweet)
        latest_tweet = get_latest_tweet()

        # Now we can chain the following tweets onto the first tweet
        get_top_artist_information(top, latest_tweet)

    elif type == 'track':
        top = user.get_top_tracks(period=time_frame)
        first_tweet = "My most listened to #Tracks of the last {}".format(
            [value for key, value in time_frames.items() if time_frame in key.lower()][0])
        print(first_tweet, flush=True)

        if tweet:
            api.update_status(status=first_tweet)
        latest_tweet = get_latest_tweet()

        get_top_track_information(top, latest_tweet)

    elif type == 'album':
        top = user.get_top_albums(period=time_frame)

    if tweet:
        api.update_status(status=tweet)


def search_spotify(search_string, type):
    result = sp.search(search_string, limit='1', type=type)
    if type == 'artist':
        result = result['artists']['items']
    elif type == 'track':
        None
    url = ''
    for item in result:
        url = item['external_urls']
        url = url.get('spotify')
    return url


def get_top_artist_information(list_of_artists, latest_tweet):
    tweet_count = 1
    for artist in list_of_artists:

        artist_name = str(artist[0])
        if include_twitter_handles:
            artist_name = twitter_handles.is_artist_in_dict(artist_name)
        playcount = str(artist[1])

        add_to_tweet = "{}. {} - {}{} \n{}".format(tweet_count, artist_name, playcount, PLAYS,
                                                   search_spotify(artist_name, 'artist'))
        if tweet:
            api.update_status(status=add_to_tweet, in_reply_to_status_id=latest_tweet)
            latest_tweet = get_latest_tweet()
            sleep(10)

        print(add_to_tweet, flush=True)

        tweet_count += 1
        if tweet_count > limit:
            break


def check_number(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid int value. The minimum value has to be one or more" % value)
    return ivalue


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
parser.add_argument("-a", "--at",
                    help="Include this at runtime to replace mentions of artists names with their twitter handles (if they are stored)",
                    action="store_true")
parser.add_argument("-t", "--tweet",
                    help="Used to turn tweeting off, usually used for testing purposes",
                    action="store_true")
parser.add_argument("--limit", help="Specify how many tracks you want in the playlist", default=10, type=check_number)

args = parser.parse_args()

artist = args.artists
include_twitter_handles = args.at
tweet_args = args.tweet
limit = args.limit

if tweet_args:
    tweet = False
    print('Tweeting has been disabled', flush=True)
if include_twitter_handles:
    print('Artists names will be replaced with their twitter handle', flush=True)

if artist:
    gather_relevant_information_to_request('artist', artist)
