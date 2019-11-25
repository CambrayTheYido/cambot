# cambot

https://twitter.com/BotCambray

A twitter bot that collates information from a last.fm user profile to tweet about a users music listening trends. This bot can also create varying Spotify playlists based on this information.

### dynamic_playlister.py

This takes a cmd line parameter of a spotify playlist URI. It loads a users last.fm profile listening data for all date ranges possible, which are the users most listened to tracks of the last 7 days, 1 month, 3 months, 6 months, 12 months, and overall. All this data gets put into a list that is looped over and each bit of information parsed. The loop extracts the songs artist and track title and puts it into a defaultdict, along with the amount of times the user has listened to that song. The amount of times the user has listened to that song is passed into a method that increases the value based on time range of the plays. For example, if the play was in the last 7 days, it gets a boosted score in comparison to a play over the last three months. It does this so that the playlist is mainly consisting of recent listening trends, with a mix of long term trends. We don't just want a playlist of top songs over the last month, we want to give each song a score, based on a simple algorithm.
Once that has been calculated, it passes the songs onto a file that searches spotify for it. That spotify URL is passed into a list and once the list hits a length of 50 is added to the playlist originally passed into the program via the cmd line.
