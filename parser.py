from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import ssl
import pdb
import json
import html
import base64
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from time import sleep
from spotify_interface import authenticate_spotify, get_tracks_in_album, get_track, add_tracks_to_playlist

# Makes it ok to make improper ssl calls TODO: fix this in the future.
ssl._create_default_https_context = ssl._create_unverified_context

SPOTIFY_ACCESS_TOKEN = authenticate_spotify()

# I'm feeling paranoid about getting blacklisted – I'm not planning on abusing any web service, but I might accidentally.
def proxy_request(url, headers=None):
	proxy_handler = urllib.request.ProxyHandler({"http":"http://185.93.3.123:8080"})
	opener = urllib.request.build_opener(proxy_handler)
	urllib.request.install_opener(opener)
	request = urllib.request.Request(url)

	if headers is not None:
		for header in headers:
			request.add_header('Authorization', 'Basic ' + encoded.decode())


	with urllib.request.urlopen(request) as response:
		return response.read()

def remove_wierd_quotation_marks(string):
	no_quotes = string.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", '').replace(u"\u201d", '').strip()
	return html.unescape(no_quotes)

def parse_pitchfork_rss(url, after_date):
	contents = proxy_request(url)
	soup = BeautifulSoup(contents, 'xml')
	feed_res = []
	for item in soup.find_all('item'):
		title_components = item.title.text.split(':')

		# get rid of weird ascii stuff
		creator = remove_wierd_quotation_marks(title_components[0])
		song = remove_wierd_quotation_marks(title_components[1])
		parsedDate = date_parser.parse(item.pubDate.text).replace(tzinfo=None)

		# only add to the result if the review was published after the after_date.
		if after_date is None or after_date < parsedDate:
			feed_res.append({
				'creator': creator,
				'song': song,
				'link': item.link.text,
				'published': item.pubDate.text,
			})
	print(json.dumps(feed_res, indent=2))
	return feed_res

def parse_best_tracks(after_date):
	return parse_pitchfork_rss("https://pitchfork.com/rss/reviews/best/tracks/", after_date)

# Get a formatted array of the best albums section of pitchfork since given after date.
def parse_best_albums(after_date):
	return parse_pitchfork_rss("https://pitchfork.com/rss/reviews/best/albums/", after_date)

def parse_album_review(url):
	contents = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(contents, 'html.parser')
	return soup.find(attrs={'class':'review-detail__article-content'}).text


def get_mentioned_tracks(album_text, album_name, artist_name):
	tracks = get_tracks_in_album(album_name, artist_name, SPOTIFY_ACCESS_TOKEN)
	mentioned = {}
	for track_name in tracks.keys():
		if track_name in album_text:
			mentioned.update({track_name: tracks[track_name]})
	return mentioned

def get_best_new_tracks():
	tracks = parse_best_tracks(datetime.now()-timedelta(days=20))
	trackDict = {}
	for track in tracks:
		spotfy_track = get_track(track['song'], track['creator'], SPOTIFY_ACCESS_TOKEN)
		if spotfy_track is None:
			trackDict[track['song']] = None
		else:
			trackDict.update(spotfy_track)
		sleep(0.5)
	return trackDict

def get_playlist_songs():
	bestAlbums = parse_best_albums(datetime.now()-timedelta(days=20))
	sleep(2)
	all_mentioned_tracks = {}
	for album in bestAlbums:
		album_review = parse_album_review(album['link']).strip()
		mentioned = get_mentioned_tracks(album_review, album['song'].strip(), album['creator'].strip())
		all_mentioned_tracks.update(mentioned)

		# Be a responsible client
		sleep(0.5)
	return all_mentioned_tracks


best_new_tracks = get_best_new_tracks()
track_uris = []
for key in best_new_tracks.keys():
	if best_new_tracks[key] is not None:
		track_uris.append(best_new_tracks[key])
best_album_tracks = get_playlist_songs()
for key in best_album_tracks.keys():
	if best_album_tracks[key] is not None:
		track_uris.append(best_album_tracks[key])
add_tracks_to_playlist('5RNnDzAFYdQNPzFYZAbSR3', track_uris, SPOTIFY_ACCESS_TOKEN)



