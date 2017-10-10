import pylast
import sys
from twython import Twython
import config

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

# Twitter object
api = Twython(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret)

# LastFM network objects
network = pylast.LastFMNetwork(api_key=last_fm_api_key, api_secret=last_fm_api_secret, username=last_fm_username,
                               password_hash=pylast.md5(last_fm_password))
user = network.get_user(last_fm_username)


class CustomUser(pylast.User):
    def __init__(self, *args, **kwargs):
        super(CustomUser, self).__init__(*args, **kwargs)

    def _get_things(
            self, method, thing, thing_type, params=None, cacheable=True
    ):
        """Returns a list of the most played thing_types by this thing."""

        from pylast import TopItem, _extract, _number
        doc = self._request(
            self.ws_prefix + "." + method, cacheable, params)

        toptracks_node = doc.getElementsByTagName('toptracks')[0]
        total_pages = int(toptracks_node.getAttribute('totalPages'))

        seq = []
        for node in doc.getElementsByTagName(thing):
            title = _extract(node, "name")
            artist = _extract(node, "name", 1)
            mbid = _extract(node, "mbid")
            playcount = _number(_extract(node, "playcount"))

            thing = thing_type(artist, title, self.network)
            thing.mbid = mbid
            seq.append(TopItem(thing, playcount))

        return seq, total_pages

    def get_top_tracks(
            self, period=pylast.PERIOD_7DAYS, limit=3, page=1, cacheable=True):
        """Returns the top tracks played by a user.
        * period: The period of time. Possible values:
          o PERIOD_OVERALL
          o PERIOD_7DAYS
          o PERIOD_1MONTH
          o PERIOD_3MONTHS
          o PERIOD_6MONTHS
          o PERIOD_12MONTHS
        """

        params = self._get_params()
        params['period'] = period
        params['page'] = page
        if limit:
            params['limit'] = limit

        return self._get_things(
            "getTopTracks", "track", pylast.Track, params, cacheable)


my_user = CustomUser(config.lastfm_username, network)
params = my_user._get_params()
params['period'] = pylast.PERIOD_7DAYS
params['limit'] = 2

tweetStr = ""

page = 1
results, total_pages = my_user.get_top_tracks(page=page)
# print total_pages
while len(results) != 0:
    count = 0
    for track in results:
        trackTitle = track.item.title
        trackArtist = track.item.artist
        trackPlays = track.weight
        toTweet = str(trackTitle) + " - " + str(trackArtist) + "\n"
        if len(tweetStr) + len(toTweet) <= 119:
            tweetStr += toTweet
        else:
            break
    page += 1
    results, total_pages = my_user.get_top_tracks(page=page)
    if (page >= 2):
        break

topThree = "#TopTracksOfTheWeek\n"
tweetStr = topThree + tweetStr

api.update_status(status=tweetStr)
