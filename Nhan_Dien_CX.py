import cv2
print(f"OpenCV version: {cv2.__version__}")
import numpy as np
from datetime import datetime
import os

class EmotionDetector:
    def __init__(self):
        # Khởi tạo các cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        # Tạo thư mục để lưu ảnh
        self.output_dir = 'emotion_captures'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Khởi tạo biến đếm frame
        self.frame_count = 0
        self.emotion_history = []

    def analyze_facial_features(self, face_roi_gray):
        # Phân tích độ sáng và độ tương phản
        brightness = np.mean(face_roi_gray)
        contrast = np.std(face_roi_gray)
        return brightness, contrast

    def detect_emotion(self, face_roi_gray, eyes, smiles, brightness, contrast):
        # Khởi tạo điểm cho các cảm xúc
        emotion_scores = {
            'Vui ve': 0,
            'Buon': 0,
            'Binh thuong': 0,
            'Ngac nhien': 0,
            'Met moi': 0
        }

        # Phân tích dựa trên số lượng mắt phát hiện được
        if len(eyes) >= 2:
            emotion_scores['Binh thuong'] += 1
        elif len(eyes) == 0:
            emotion_scores['Met moi'] += 1

        # Phân tích dựa trên nụ cười
        if len(smiles) > 0:
            emotion_scores['Vui ve'] += 2

        # Phân tích dựa trên độ sáng và độ tương phản
        if brightness < 100:  # Khuôn mặt tối
            emotion_scores['Buon'] += 1
        if contrast > 50:  # Độ tương phản cao
            emotion_scores['Ngac nhien'] += 1

        # Xác định cảm xúc chiếm ưu thế
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        return dominant_emotion, emotion_scores

    def get_emotion_color(self, emotion):
        # Màu sắc cho từng cảm xúc
        color_map = {
            'Vui ve': (0, 255, 0),    # Xanh lá
            'Buon': (0, 0, 255),      # Đỏ
            'Binh thuong': (255, 255, 0),  # Vàng
            'Ngac nhien': (255, 165, 0),   # Cam
            'Met moi': (128, 0, 128)   # Tím
        }
        return color_map.get(emotion, (200, 200, 200))

    def save_emotion_capture(self, frame, emotion):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/emotion_{emotion}_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Đã lưu ảnh: {filename}")

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Trích xuất vùng khuôn mặt
            face_roi_gray = gray[y:y+h, x:x+w]
            face_roi_color = frame[y:y+h, x:x+w]

            # Phát hiện đặc điểm khuôn mặt
            eyes = self.eye_cascade.detectMultiScale(face_roi_gray)
            smiles = self.smile_cascade.detectMultiScale(face_roi_gray, 1.7, 20)

            # Phân tích đặc điểm khuôn mặt
            brightness, contrast = self.analyze_facial_features(face_roi_gray)

            # Nhận diện cảm xúc
            emotion, scores = self.detect_emotion(face_roi_gray, eyes, smiles, brightness, contrast)

            # Vẽ khung khuôn mặt
            color = self.get_emotion_color(emotion)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)

            # Hiển thị thông tin
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, f"Cam xuc: {emotion}", (x, y-10), font, 0.9, color, 2)

            # Hiển thị các điểm số cảm xúc
            y_offset = y + h + 20
            for emotion_name, score in scores.items():
                text = f"{emotion_name}: {score}"
                cv2.putText(frame, text, (x, y_offset), font, 0.6, self.get_emotion_color(emotion_name), 2)
                y_offset += 20

            # Lưu ảnh mỗi 30 frame nếu phát hiện cảm xúc rõ ràng
            self.frame_count += 1
            if self.frame_count % 30 == 0 and scores[emotion] >= 2:
                self.save_emotion_capture(frame, emotion)

            # Vẽ đặc điểm mắt
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(face_roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            # Vẽ đặc điểm nụ cười
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(face_roi_color, (sx, sy), (sx+sw, sy+sh), (255, 0, 0), 2)

        return frame

def open_camera():
    detector = EmotionDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở camera")
        return

    print("Nhấn 'q' để thoát, 's' để chụp ảnh")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Không thể nhận frame từ camera")
            break

        # Xử lý frame
        processed_frame = detector.process_frame(frame)

        # Hiển thị frame
        cv2.imshow('He thong nhan dien cam xuc', processed_frame)

        # Xử lý phím bấm
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Chụp ảnh thủ công
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{detector.output_dir}/manual_capture_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Đã chụp ảnh: {filename}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    open_camera()

# Chạy chương trình