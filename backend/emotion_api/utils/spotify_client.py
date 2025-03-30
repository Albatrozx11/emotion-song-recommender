import requests
import logging
import os
import sys
import base64
import json
from dotenv import load_dotenv

load_dotenv()
# Import your existing token fetching code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

logger = logging.getLogger(__name__)

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
    
    if result.status_code != 200:
        logger.error(f"Failed to obtain Spotify token: {result.text}")
        raise Exception("Failed to obtain Spotify token")
    
    json_result = json.loads(result.text)
    token = json_result["access_token"]
    return token

def get_playlist_tracks(playlist_id):
    """Get tracks from a Spotify playlist using the existing token function"""
    try:
        # Use your existing token function
        token = get_token()
        logger.info(f"Token obtained: {token[:10]}...")  # Log first 10 chars for security
        
        if not token:
            logger.error("Empty token received from get_token()")
            return []
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        logger.info(f"Fetching tracks for playlist: {playlist_id}")
        response = requests.get(url, headers=headers)
        
        # Log the response status and first part of response for debugging
        logger.info(f"Spotify API response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Spotify API error: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        if 'items' not in data:
            logger.error(f"Unexpected response format: {data}")
            return []
            
        tracks = []
        for item in data['items']:
            if 'track' not in item or item['track'] is None:
                continue
                
            track = item['track']
            
            # Extract all artists names
            artists = [artist['name'] for artist in track['artists']] if 'artists' in track else []
            artist_names = ", ".join(artists)
            
            # Get the preview URL
            preview_url = track.get('preview_url', None)
            
            # Get album images (if available)
            album_images = []
            if 'album' in track and 'images' in track['album']:
                album_images = track['album']['images']
            
            # Format the track data to match what the frontend expects
            track_data = {
                'id': track.get('id', ''),
                'name': track.get('name', 'Unknown Title'),
                'artists': [{'name': name} for name in artists],
                'album': {
                    'name': track.get('album', {}).get('name', 'Unknown Album'),
                    'images': album_images
                },
                'preview_url': preview_url
            }
            
            tracks.append(track_data)
            
        logger.info(f"Retrieved {len(tracks)} tracks from playlist")
        return tracks
        
    except Exception as e:
        logger.error(f"Failed to fetch Spotify playlist tracks: {str(e)}")
        raise
