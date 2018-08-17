# BandBringerBot
Scrapes music reviews and makes playlists to bring me bands. You can follow it here: https://open.spotify.com/user/kkraqvb1hnm15147lwcpqayc1

Written in Python3. Right now the bot only scrapes pitchfork's best new albums and best new tracks sections for the past 20 days.

## Super Great Features:
* Doesn't add full albums to playlists, but reads through the album review and searches for tracks that are explicitly mentioned to add to the playlist.
* Uses a proxy server to access the music review and spotify apis. This is not because I want to abuse these platforms, but because I know that it is possible that I will accidentally mess up and get blacklisted. I use spotify pretty often and would prefer not to be blocked.

## Super Great Potential Features:
* Pitchfork is the only music review site that is supported. Add more! Pitchfork was super easy because they have an rss feed—hopefully others will too.
* Some sort of automation of authentication. You can certainly clone this and create your own bandbringerbot, but you'll have to set it up with spotify yourself. This bot only takes the refresh token obtained from [this authorization flow](https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow)
* Run the bot periodically——maybe a cron job?
* Do sentiment analysis on album reviews to determine what tracks are good.
* Look for different band names in album reviews and create a playlist for the album with some connected bands and singles that are related according to the reviews.
