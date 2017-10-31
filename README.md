# cambot
Twitter bot that uses APIs such as Spotipy; a python wrapper for the Spotify web API and pylast; a python wrapper for the last.fm web API.

### dailySpotifyCount.py 

This script runs at 23.59 daily and collects all the songs I have potentially listened to and gets the length of that list. This length is set to a count variable which is then tweeted as how many songs I have listened to on spotify that day.

### nowPlaying.py 

This runs constantly, checking every 15 seconds if what I am currently listening to has changed, and then tweets about it.

### topAlbumsOfTheWeek.py

This runs once a week on a sunday and collects my top albums I have been listening to on Spotify. This then collects as many albums as it can before hitting the 140 character limit.

### topAlbumUpdate

This is run every 30 mins and checks if my most listened to album of the last 7 days has changed from what it last tweeted.

### topArtistUpdate

This is run every 30 mins and checks if my most listened to artist of the last 7 days has changed from what it last tweeted.

### topTrackUpdate.py

This is run every 30 mins and checks if my most listened to track of the last 7 days has changed from what it last tweeted.

### topTracksLongTerm.py

This gets my top tracks from over the last few years using the Spotify API and then tweets them in order of most played.

### topTracksMediumTerm.py

This gets my top tracks from over the last 6 months using the Spotify API and then tweets them in order of most played.

### topTracksShortTerm.py

This gets my top tracks from over the last month using the Spotify API and then tweets them in order of most played.