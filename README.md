# cambot

https://twitter.com/BotCambray

A twitter bot that collates information from a last.fm user profile to tweet about a users music listening trends. This bot can also create varying Spotify playlists based on this information.

Dependencies:
pylast
spotipy
argparse
twython
pymongo
python-dateutil

See Pipfile for dependency versions.

### dynamic_playlister.py

This takes a cmd line parameter of a spotify playlist URI. It loads a users last.fm profile listening data for all date ranges possible, which are the users most listened to tracks of the last 7 days, 1 month, 3 months, 6 months, 12 months, and overall. All this data gets put into a list that is looped over and each bit of information parsed. The loop extracts the songs artist and track title and puts it into a defaultdict, along with the amount of times the user has listened to that song. The amount of times the user has listened to that song is passed into a method that increases the value based on time range of the plays. For example, if the play was in the last 7 days, it gets a boosted score in comparison to a play over the last three months. It does this so that the playlist is mainly consisting of recent listening trends, with a mix of long term trends. We don't just want a playlist of top songs over the last month, we want to give each song a score, based on a simple algorithm.
Once that has been calculated, it passes the songs onto a file that searches spotify for it. That spotify URL is passed into a list and once the list hits a length of 50 is added to the playlist originally passed into the program via the cmd line.

here is an output of the ordered dict this produces. The key is the artist and track name and the value is the score assigned to the track based on listening trends, which all depends on how much weight you assign to each timeframe.

![Dynamic_playlist_algorithm_score](https://raw.githubusercontent.com/ryancambray/cambot/master/examples/dynamic_playlist_example.PNG)

Playlist here: https://open.spotify.com/playlist/09mHNJgzOgdUZksMrohoPH?si=M92bCkByTm2UMf1s7_l77w

### top_artists_songs_albums_updates.py	
Can tweet single tweets or create threads of lists of songs/artists/albums over the last x amount of time.

Single tweet:

![Singular Tweet](https://raw.githubusercontent.com/ryancambray/cambot/master/examples/cambotexample.JPG)

Thread:

![Thread of Tweets](https://github.com/ryancambray/cambot/blob/master/examples/thread.JPG?raw=true)

### top_tracks_playlister.py
Uses built in Spotify API calls to create playlists of most listened to songs over the last month, few months, and years.

Example over the last month:

![Top tracks of september](https://github.com/ryancambray/cambot/blob/master/examples/Capture.JPG?raw=true)

Last few years:

![Last few years](https://github.com/ryancambray/cambot/blob/master/examples/years.JPG?raw=true)
