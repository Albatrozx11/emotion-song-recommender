# emotion_api/views.py
import cv2
import numpy as np
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from .utils.emotion_detector import detect_emotion
from django.http import JsonResponse
from django.conf import settings
from .utils.spotify_client import get_playlist_tracks
logger = logging.getLogger(__name__)
SPOTIFY_PLAYLISTS = {
    'Happy': '37i9dQZF1EIgG2NEOhqsD7',  # Replace with your actual playlist IDs
    'Sad': '37i9dQZF1DX7qK8ma5wgG1',
    'Neutral': '37i9dQZF1DX2Nc3B70tvx0',
    'Angry': '37i9dQZF1DX1rVvRgjX59F',
    'Surprise': '37i9dQZF1DX4fpCWaHpNic',
    'Fear': '37i9dQZF1DX0XUsuxWHRQd'
}
@api_view(['POST'])
@csrf_exempt
def detect_emotion_view(request):
    """
    Handle emotion detection requests with validation and error handling
    """
    try:
        # 1. Validate request contains an image file
        if 'image' not in request.FILES:
            logger.error("No image file in request")
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        # 2. Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if image_file.size > max_size:
            logger.error(f"File too large: {image_file.size} bytes")
            return Response({'error': 'File too large (max 5MB)'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # 3. Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image_file.content_type not in allowed_types:
            logger.error(f"Invalid file type: {image_file.content_type}")
            return Response({'error': 'Invalid file type (JPEG/PNG only)'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # 4. Read and decode image
        try:
            image_bytes = image_file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image")
                return Response({'error': 'Invalid image file'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return Response({'error': 'Invalid image data'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # 5. Detect emotion
        try:
            emotion = detect_emotion(image)
            if emotion == 'no_face':
                logger.warning("No face detected in image")
                return Response({'error': 'No face detected'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Emotion detection failed: {str(e)}")
            return Response({'error': 'Emotion detection failed'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return Response({
            'emotion': emotion,
        })

    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return Response({'error': 'Internal server error'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_music_recommendations(request, emotion):
    """
    Get music recommendations from Spotify based on detected emotion
    
    Parameters:
    - emotion: The detected emotion (Happy, Sad, Neutral, etc.)
    """
    try:
        # Validate emotion
        valid_emotions = ['Happy', 'Sad', 'Neutral', 'Angry', 'Surprise', 'Fear']
        if emotion not in valid_emotions:
            return Response({'error': 'Invalid emotion'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get Spotify recommendations
        if emotion not in SPOTIFY_PLAYLISTS:
            return Response({'error': f'No music recommendations for {emotion}'}, 
                          status=status.HTTP_404_NOT_FOUND)
                
        playlist_id = SPOTIFY_PLAYLISTS[emotion]
        tracks = get_playlist_tracks(playlist_id)
        
        return Response({
            'emotion': emotion,
            'tracks': tracks
        })
    
    except Exception as e:
        logger.error(f"Error getting music recommendations: {str(e)}")
        return Response({'error': 'Failed to get music recommendations'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)