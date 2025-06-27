import os
import time
import json
import cv2
import requests
from datetime import datetime

from src.main.emotion_detection import EmotionDetectionSystem

SERVER_URL = "http://localhost:5000/api/camera-emotion"  # Endpoint của giáo viên
STUDENT_ID = "student01"
INTERVAL = 5  # giây giữa các lần phân tích


def analyze_and_send(system, frame):
    """Phân tích cảm xúc và gửi kết quả tới server"""
    temp_path = "temp_student_frame.jpg"
    cv2.imwrite(temp_path, frame)
    result = system.analyze_emotion_from_image(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)

    payload = {
        "student_id": STUDENT_ID,
        "timestamp": datetime.now().isoformat(),
        "result": result,
    }
    try:
        requests.post(SERVER_URL, json=payload, timeout=2)
    except Exception as exc:
        print(f"Lỗi gửi dữ liệu: {exc}")


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Không thể mở camera")
        return

    system = EmotionDetectionSystem()
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Không đọc được frame")
                break
            analyze_and_send(system, frame)
            time.sleep(INTERVAL)
    finally:
        cap.release()


if __name__ == "__main__":
    main()
