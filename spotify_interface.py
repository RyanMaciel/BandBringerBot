import base64
import urllib.request
import urllib.parse
import json
import pdb
from time import sleep


# time to uid 
WAIT_TIME = 0.5


# I know there are packages to do this, but I don't need anything complicated.
# This populates secrets from a file called environment_variables.txt which has the format: VARIABLE=VALUE

CLIENT_ID = ''
CLIENT_SECRET = ''
REFRESH_TOKEN = ''
BOT_USER_ID = ''
with open('environment_variables.txt') as f:
	for line in f:
		variable_components = line.strip().split('=')
		if variable_components[0] == 'CLIENT_ID':
			CLIENT_ID = variable_components[1]
		if variable_components[0] == 'CLIENT_SECRET':
			CLIENT_SECRET = variable_components[1]
		if variable_components[0] == 'REFRESH_TOKEN':
			REFRESH_TOKEN = variable_components[1]
		if variable_components[0] == 'BOT_USER_ID':
			BOT_USER_ID = variable_components[1]


def get_track(track_name, artist, access_token):
	track_search_data = search(track_name + ' ' + artist, artist, 'track', access_token)

	###### TODO deal with [feat. aslkdfdjsalf] in song title labels
	# retry without the artist name (sometimes the reviews call the artists something different than spotify)
	if track_search_data is None:
		sleep(WAIT_TIME)
		track_search_data = search(track_name, artist, 'album', access_token)

	if track_search_data is None:
		return None
	return {track_search_data['name']: track_search_data['uri']}
	

def get_tracks_in_album(album_name, artist, access_token):
	album_search_data = search(album_name + ' ' + artist, artist, 'album', access_token)

	# retry without the artist name (sometimes the reviews call the artists something different than spotify)
	if album_search_data is None:
		sleep(WAIT_TIME)
		album_search_data = search(album_name, artist, 'album', access_token)
	try:
		request = urllib.request.Request('https://api.spotify.com/v1/albums/' + urllib.parse.quote_plus(album_search_data['id']))
		request.add_header('Authorization', 'Bearer ' + access_token)
		responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')
		tracks_json = json.loads(responseData)['tracks']['items']

		# dictionary {<trackName>: <trackkey>}
		track_ids = {}
		for track_json in tracks_json:
			track_ids[track_json['name']] = track_json['uri']
		return track_ids
	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False

def search(term, artist, type, access_token):
	try:
		request = urllib.request.Request('https://api.spotify.com/v1/search?q=' + urllib.parse.quote_plus(term) + '&type=' + type)
		request.add_header('Authorization', 'Bearer ' + access_token)
		responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')

		albums = json.loads(responseData)[type + 's']['items']
		for album_entry in albums:
			# watch out for case sensitivity
			if album_entry['artists'][0]['name'].lower() == artist.lower():
				return album_entry
		return None

	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False

def user_authenticate():
	try:
		url = 'https://accounts.spotify.com/authorize/?'
		url_params = 'client_id=' + CLIENT_ID + '&response_type=code&redirect_uri='
		url_params += urllib.parse.quote_plus('https://example.com/callback') + '&scope=' + urllib.parse.quote_plus('playlist-modify-public')

		#request = urllib.request.Request(url)
		#responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')
		return url + url_params

	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False

def add_tracks_to_playlist(playlist_id, track_uris, access_token):
	try:
		details = {
			'uris': track_uris,
		}
		details = json.dumps(details).encode('utf-8')
		request = urllib.request.Request('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', details)
		request.add_header('Authorization', 'Bearer ' + access_token)
		request.add_header('Content-Type', 'application/json')
		request.add_header('Content-Length', len(details))
		request.get_method = lambda: 'PUT'
		responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')
		return json.loads(responseData)
	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False
def create_playlist(name, access_token):
	try:
		details = {
			'name': name,
		}
		details = json.dumps(details).encode('utf-8')
		request = urllib.request.Request('https://api.spotify.com/v1/users/' + BOT_USER_ID + '/playlists', details)
		request.add_header('Authorization', 'Bearer ' + access_token)
		request.add_header('Content-Type', 'application/json')
		request.add_header('Content-Length', len(details))
		responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')
		return json.loads(responseData)
	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False

# refresh the auth token using the refresh token. Should set up a utility to allow the user to enter the authorization code from the spotify redirect thing
# and handle fetching the auth code, but that is for later.
# doing the redirect flow, the code only works for one auth token and then you need to refesh it
def authenticate_spotify():
	try:
		details = urllib.parse.urlencode({
			'grant_type': 'refresh_token',
			'refresh_token': REFRESH_TOKEN,
		})
		details = details.encode()
		request = urllib.request.Request('https://accounts.spotify.com/api/token', details)
		encoded = base64.b64encode(bytes(CLIENT_ID + ':' + CLIENT_SECRET, 'utf-8'))
		request.add_header('Authorization', 'Basic ' + encoded.decode())
		responseData = urllib.request.urlopen(request).read().decode('utf8', 'ignore')
		return json.loads(responseData)['access_token']

	except urllib.error.HTTPError as e:
		responseData = e.read().decode('utf8', 'ignore')
		print(responseData)
		responseFail = False
