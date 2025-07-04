import os
from deepface import DeepFace
import cv2
import numpy as np

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'emotion_model.h5')

EMOTIONS = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprised']

# Bản đồ cảm xúc sang tiếng Việt
EMOTION_VI = {
    'angry': 'Tức giận',
    'contempt': 'Khinh bỉ',
    'disgust': 'Ghê tởm',
    'fear': 'Sợ hãi',
    'happy': 'Vui vẻ',
    'neutral': 'Bình thường',
    'sad': 'Buồn',
    'surprise': 'Ngạc nhiên',
    'surprised': 'Ngạc nhiên',
    'anger': 'Tức giận',
    'contempt': 'Khinh bỉ',
}

# Hàm nhận diện cảm xúc từ ảnh (numpy array)
def predict_emotion(img):
    result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
    if not result or not isinstance(result, list) or not result or not isinstance(result[0], dict):
        return "Không nhận diện được"
    emotion_en = result[0]['dominant_emotion'] if 'dominant_emotion' in result[0] else None
    if not emotion_en:
        return "Không nhận diện được"
    emotion_vi = EMOTION_VI.get(emotion_en.lower(), emotion_en)
    return emotion_vi 