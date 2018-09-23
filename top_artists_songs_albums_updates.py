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
import os

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
add_to_database = False

NO_UPDATE_NEEDED = "Information up to date and already tweeted."


def get_latest_tweet():
    the_latest_tweet = None
    while the_latest_tweet is None:
        the_latest_tweet = api.get_user_timeline(screen_name="BotCambray")
        the_latest_tweet = the_latest_tweet[0].get('id')
    return the_latest_tweet

def singular_top_artist_update(period, top):
    for x in top:
        search_str = str(x[0])

    artist_url = search_spotify(search_str, 'artist')

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topArtistUpdate7day.txt"
        top_artist_time_frame = "#TopArtistOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topArtistUpdate1month.txt"
        top_artist_time_frame = "New #TopArtistUpdate of the month"
    elif period == "3month":
        file_name = "topArtistUpdate3month.txt"
        top_artist_time_frame = "New #TopArtistUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topArtistUpdate6month.txt"
        top_artist_time_frame = "New #TopArtistUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topArtistUpdate12month.txt"
        top_artist_time_frame = "New #TopArtistUpdate of the last year"
    elif period == "overall":
        file_name = "topArtistUpdateOverall.txt"
        top_artist_time_frame = "New #TopArtistUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search_str:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search_str)
        file.close()
        tweetStr = top_artist_time_frame + "\n\n" + search_str + "\n" + str(artist_url)
        print(tweetStr, flush=True)
        try:
            if tweet:
                api.update_status(status=tweetStr)
                # Just to reduce the spam load a little.
                sleep(5)
        except:
            print("Could not tweet latest Artist update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()

def singular_top_track_update(period, top):
    for x in top:
        search_str = str(x[0])

    track_url = search_spotify(search_str, 'track')

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topTrackUpdate7day.txt"
        top_track_time_frame = "#TopTrackOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topTrackUpdate1month.txt"
        top_track_time_frame = "New #TopTrackUpdate of the month"
    elif period == "3month":
        file_name = "topTrackUpdate3month.txt"
        top_track_time_frame = "New #TopTrackUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topTrackUpdate6month.txt"
        top_track_time_frame = "New #TopTrackUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topTrackUpdate12month.txt"
        top_track_time_frame = "New #TopTrackUpdate of the last year"
    elif period == "overall":
        file_name = "topTrackUpdateOverall.txt"
        top_track_time_frame = "New #TopTrackUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search_str:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search_str)
        file.close()
        tweet_str = top_track_time_frame + "\n\n" + search_str + "\n" + str(track_url)
        print(tweet_str, flush=True)
        try:
            if tweet:
                api.update_status(status=tweet_str)
                # Just to reduce the spam load a little.
                sleep(5)
        except:
            print("Could not tweet latest track update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()

def singular_top_album_update(period, top):
    for x in top:
        search = str(x[0])

    album_url = search_spotify(search, 'album')

    # Check if the information has already been tweeted lately, if not then tweet new update
    path = os.getcwd()

    # find out which file we are checking for the time frame chosen
    if period == "7day":
        file_name = "topAlbumUpdate7day.txt"
        top_album_time_frame = "#TopAlbumOfTheWeekUpdate"
    elif period == "1month":
        file_name = "topAlbumUpdate1month.txt"
        top_album_time_frame = "New #TopAlbumUpdate of the month"
    elif period == "3month":
        file_name = "topAlbumUpdate3month.txt"
        top_album_time_frame = "New #TopAlbumUpdate of the last 3 months"
    elif period == "6month":
        file_name = "topAlbumUpdate6month.txt"
        top_album_time_frame = "New #TopAlbumUpdate of the last 6 months"
    elif period == "12month":
        file_name = "topAlbumUpdate12month.txt"
        top_album_time_frame = "New #TopAlbumUpdate of the last year"
    elif period == "overall":
        file_name = "topAlbumUpdateOverall.txt"
        top_album_time_frame = "New #TopAlbumUpdate of all time (tracking since Jun 2016)"

    file_name_and_path = path + "\\" + file_name

    file = open(file_name_and_path, "a+")
    file.seek(0)

    if file.read() != search:
        file.close()
        file = open(file_name_and_path, "w+")
        file.write(search)
        file.close()
        tweetStr = top_album_time_frame + "\n\n" + search + "\n" + str(album_url)
        print(tweetStr, flush=True)
        try:
            if tweet:
                api.update_status(status=tweetStr)
                # Just to reduce the spam load a little.
                sleep(5)
        except:
            print("Could not tweet latest track update", flush=True)
    else:
        print(NO_UPDATE_NEEDED, flush=True)
        file.close()

def gather_relevant_information(type, time_frame, limit):
    if type == 'artist':
        # determine period to use
        top = user.get_top_artists(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Artists of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            # Tweet the first tweet to get the ball rolling, grab the ID of the tweet while we're at it
            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            # Now we can chain the following tweets onto the first tweet
            chain_updates(top, latest_tweet, type)
        else:
            singular_top_artist_update(time_frame, top)

    elif type == 'track':
        top = user.get_top_tracks(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Tracks of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            chain_updates(top, latest_tweet, type)
        else:
            singular_top_track_update(time_frame, top)

    elif type == 'album':
        top = user.get_top_albums(period=time_frame, limit=limit)

        if limit > 1:
            first_tweet = "My top {} most listened to #Albums of the last {}".format(limit,
                [value for key, value in time_frames.items() if time_frame in key.lower()][0])
            print(first_tweet, flush=True)

            if tweet:
                api.update_status(status=first_tweet)
            latest_tweet = get_latest_tweet()

            chain_updates(top, latest_tweet, type)
        else:
            singular_top_album_update(time_frame, top)

def search_spotify(search_string, type):
    result = sp.search(search_string, limit='1', type=type)
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

def chain_updates(list_of_top_items, latest_tweet, type):
    tweet_count = 1
    for top_item in list_of_top_items:

        track_artist_album_search = str(top_item[0])
        track_artist_album = str(top_item[0])
        if include_twitter_handles and type == 'artist':
            track_artist_album = twitter_handles.check_or_add_artist_names_to_database(track_artist_album, add_to_database)
        playcount = str(top_item[1])

        add_to_tweet = "{}. {} - {}{} \n{}".format(tweet_count, track_artist_album, playcount, PLAYS,
                                                   search_spotify(track_artist_album_search, type))
        if tweet and add_to_tweet != 'True':

            api.update_status(status=add_to_tweet, in_reply_to_status_id=latest_tweet)
            latest_tweet = get_latest_tweet()
            sleep(30)

        print(add_to_tweet, flush=True)

        tweet_count += 1
        if tweet_count > limit:
            break

def check_number(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid int value. The minimum value has to be one or more" % value)
    return ivalue


choices = ["7day", "1month", "3month", "6month", "12month", "overall", "all"]

parser = argparse.ArgumentParser()
parser.add_argument("--tracks",
                    help="Tweets the top tracks from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script", choices=choices)
parser.add_argument("--albums",
                    help="Tweets the top albums from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script",
                    choices=choices)
parser.add_argument("--artists",
                    help="Tweets the top artists from the specified time frame and, if the limit is larger than one, chains the tweets in a thread. Else it just tweets a singular update if the item has changed since you last ran the script",
                    choices=choices)
parser.add_argument("-a", "--at",
                    help="Include this at runtime to replace mentions of artists names with their twitter handles. If add is selected, you will be prompted to enter twitter handles of the corresponding artist if it was not found in the database.", default="leave", choices=['add', 'leave'])
parser.add_argument("-t", "--tweet",
                    help="Used to turn tweeting off, usually used for testing purposes",
                    action="store_true")
parser.add_argument("--limit", help="Specify how many items you want to tweet. If the limit is one then it checks your last update and if it has changed then it will tweet", default=10, type=check_number)

args = parser.parse_args()

artist = args.artists
track = args.tracks
album = args.albums

include_twitter_handles = args.at
tweet_args = args.tweet
limit = args.limit

if tweet_args:
    tweet = False
    print('Tweeting has been disabled', flush=True)
if include_twitter_handles:
    print('Artists names will be replaced with their twitter handle', flush=True)
    if include_twitter_handles == "add":
        # Add to the database
        add_to_database = True

if artist != None:
    if artist == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('artist', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('artist', artist, limit)

if track != None:
    if track == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('track', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('track', track, limit)

if album != None:
    if album == "all":
        for choice in choices:
            if choice == "all":
                break
            gather_relevant_information('album', choice, limit)
            if limit > 1:
                sleep(30)
    else:
        gather_relevant_information('album', album, limit)