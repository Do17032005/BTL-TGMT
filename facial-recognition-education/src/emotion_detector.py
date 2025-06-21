import cv2
import numpy as np
from datetime import datetime
import os

class EmotionDetector:
    def __init__(self):
        


        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        self.output_dir = 'emotion_captures'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.frame_count = 0

    def analyze_facial_features(self, face_roi_gray):
        brightness = np.mean(face_roi_gray)
        contrast = np.std(face_roi_gray)
        return brightness, contrast

    def detect_emotion(self, face_roi_gray, eyes, smiles, brightness, contrast):
        # Khởi tạo tất cả các cảm xúc với giá trị 0
        emotion_scores = {
            'vui': 0,
            'buon': 0,
            'ngac_nhien': 0,
            'tuc_gian': 0,
            'binh_thuong': 0
        }

        if len(eyes) >= 2:
            emotion_scores['vui'] += 1
        elif len(eyes) == 0:
            emotion_scores['buon'] += 1
        if len(smiles) > 0:
            emotion_scores['vui'] += 2
        if brightness < 100:
            emotion_scores['buon'] += 1
        if contrast > 50:
            emotion_scores['ngac_nhien'] += 1
        # Thêm cảm xúc 'tuc_gian' nếu có dấu hiệu tức giận
        if brightness > 200 and contrast < 20:
            emotion_scores['tuc_gian'] += 1
        else:
            emotion_scores['binh_thuong'] += 1
             # Xác định cảm xúc chiếm ưu thế 

        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        return dominant_emotion, emotion_scores

    def get_emotion_color(self, emotion):
        color_map = {
            'Vui vẻ': (0, 255, 0),  # Xanh lá
            'Buồn': (255, 0, 0),    # Xanh dương
            'Bình thường': (0, 255, 255),  # Vàng
            'Ngạc nhiên': (255, 0, 255),  # Hồng
            'Mệt mỏi': (0, 0, 255),  # Đỏ
            'Khác': (200, 200, 200)  # Màu xám cho cảm xúc không xác định
        }
        return color_map.get(emotion, (200, 200, 200))

    def save_emotion_capture(self, frame, emotion):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/emotion_{emotion}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved image: {filename}")

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray)
            smiles = self.smile_cascade.detectMultiScale(face_roi_gray, 1.7, 20)

            brightness, contrast = self.analyze_facial_features(face_roi_gray)
            emotion, scores = self.detect_emotion(face_roi_gray, eyes, smiles, brightness, contrast)

            color = self.get_emotion_color(emotion)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, f"Emotion: {emotion}", (x, y-10), font, 0.9, color, 2)

            y_offset = y + h + 20
            for emotion_name, score in scores.items():
                text = f"{emotion_name}: {score}"
                cv2.putText(frame, text, (x, y_offset), font, 0.6, self.get_emotion_color(emotion_name), 2)
                y_offset += 20

            self.frame_count += 1
            if self.frame_count % 30 == 0 and scores[emotion] >= 2:
                self.save_emotion_capture(frame, emotion)

        return frame

    def gen_frames(self, camera):
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                # processed_frame = detector.process_frame(frame)
                processed_frame = frame

            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')