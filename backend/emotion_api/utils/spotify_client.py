import requests
import logging
import os
import sys
from django.conf import settings
import base64
import json
from dotenv import load_dotenv

load_dotenv()
# Import your existing token fetching code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.text)
    token =  json_result["access_token"]
    return token



logger = logging.getLogger(__name__)

def get_playlist_tracks(playlist_id):
    """Get tracks from a Spotify playlist using the existing token function"""
    try:
        # Use your existing token function
        token = get_token()
        
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tracks = []
        response_json = response.json()['items']
        
        for item in response_json:
            track = item['track']
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'] if track['album']['images'] else None
            })
            
        return tracks
    except Exception as e:
        logger.error(f"Failed to fetch Spotify playlist tracks: {str(e)}")
        raise