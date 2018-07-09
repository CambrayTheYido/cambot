import pylast
import sys
from twython import Twython
import config
import twitter_handles

# Twitter API
twitter_api_key = config.twitter_api_key
twitter_api_secret = config.twitter_api_secret
twitter_access_token = config.twitter_access_token
twitter_access_token_secret = config.twitter_access_token_secret

# LastFM API
last_fm_api_key = config.lastfm_api_key
last_fm_api_secret = config.lastfm_api_secret
last_fm_username = config.lastfm_username

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username)
user = network.get_user(last_fm_username)

tweet_str = "#TopTracksOfTheWeek\n"

topTracksWeek = user.get_top_tracks(period='7day')
count = 1
for track in topTracksWeek:
    track_and_artist = str(track[0])
    plays_of_track = str(track[1])

    artist_and_track = twitter_handles.is_artist_in_dict(track_and_artist)

    add_to_tweet = str(count) + ". " + artist_and_track + " (" + plays_of_track + " plays)\n"

    if len(add_to_tweet) + len(tweet_str) <= 280:
        tweet_str += add_to_tweet
        count+=1

api.update_status(status=tweet_str)
print(tweet_str)
