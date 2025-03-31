# emotion_api/utils/emotion_detector.py
import cv2
import numpy as np
import os
from tensorflow.keras.models import load_model

# Get absolute paths to model files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAAR_PATH = os.path.join(BASE_DIR, 'ml_models', 'haarcascade_frontalface_default.xml')
MODEL_PATH2 = os.path.join(BASE_DIR, 'ml_models', r"ferplus_model_pd_acc.h5")
# Initialize models outside function to load only once
try:
    face_cascade = cv2.CascadeClassifier(HAAR_PATH)
    if face_cascade.empty():
        raise FileNotFoundError(f"Haar cascade file not found at {HAAR_PATH}")
except Exception as e:
    print(f"Error loading Haar cascade: {str(e)}")
    raise

try:
    emotion_model = load_model(MODEL_PATH2)
except Exception as e:
    print(f"Error loading Keras model: {str(e)}")
    raise

# Verify FER-2013 label order (adjust if your model uses different order)
EMOTION_LABELS = ['sad', 'happy', 'surprise', 'disgust', 'angry', 'neutral', 'fear']

def detect_emotion(image: np.ndarray) -> str:
    """
    Processes image and returns detected emotion
    Returns 'error' if processing fails
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with adjusted parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(48, 48),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        if len(faces) == 0:
            return 'no_face'
        
        # Process first face only
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # Preprocess for model (match your model's expected input)
        resized = cv2.resize(face_roi, (48, 48))
        normalized = resized.astype('float32') / 255.0
        reshaped = np.expand_dims(normalized, axis=-1)  # Add channel dimension
        reshaped = np.expand_dims(reshaped, axis=0)     # Add batch dimension
        
        # Predict emotion
        predictions = emotion_model.predict(reshaped)
        emotion_index = np.argmax(predictions)
        return EMOTION_LABELS[emotion_index]
    
    except Exception as e:
        print(f"Error in emotion detection: {str(e)}")
        return 'error'