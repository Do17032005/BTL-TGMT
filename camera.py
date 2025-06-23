#!/usr/bin/env python3
"""
Ứng dụng Camera Real-time để nhận diện cảm xúc
Sử dụng webcam để phân tích cảm xúc theo thời gian thực
"""

import cv2
import numpy as np
import sys
import os
import time
from datetime import datetime
from src.main.emotion_detection import EmotionDetectionSystem

# Thêm đường dẫn để import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'main'))

try:
    from src.main.emotion_detection import EmotionDetectionSystem
    print("✅ Import EmotionDetectionSystem thành công")
except ImportError as e:
    print(f"❌ Lỗi import EmotionDetectionSystem: {e}")
    print("💡 Hãy đảm bảo file emotion_detection.py tồn tại trong thư mục src/main/")
    sys.exit(1)

class RealTimeEmotionDetection:
    """
    Lớp xử lý nhận diện cảm xúc real-time qua camera
    """
    
    def __init__(self, camera_index=0, detector_backend="opencv"):
        """
        Khởi tạo hệ thống nhận diện cảm xúc real-time
        
        Args:
            camera_index: Index của camera (0 là camera mặc định)
            detector_backend: Backend để detect khuôn mặt
        """
        self.camera_index = camera_index
        self.detector_backend = detector_backend
        self.emotion_system = EmotionDetectionSystem(detector_backend=detector_backend)
        
        # Khởi tạo camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Không thể mở camera với index {camera_index}")
        
        # Cấu hình camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Biến để lưu trữ kết quả
        self.current_emotion = "Unknown"
        self.emotion_confidence = 0.0
        self.face_detected = False
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Màu sắc cho các cảm xúc
        self.emotion_colors = {
            'angry': (0, 0, 255),      # Đỏ
            'disgust': (0, 128, 0),    # Xanh lá
            'fear': (128, 0, 128),     # Tím
            'happy': (0, 255, 255),    # Vàng
            'sad': (255, 0, 0),        # Xanh dương
            'surprise': (0, 255, 0),   # Xanh lá sáng
            'neutral': (128, 128, 128) # Xám
        }
        
        # Emoji cho các cảm xúc
        self.emotion_emojis = {
            'angry': '😠',
            'disgust': '🤢',
            'fear': '😨',
            'happy': '😊',
            'sad': '😢',
            'surprise': '😲',
            'neutral': '😐'
        }
        
        print(f"✅ Camera khởi tạo thành công (Index: {camera_index})")
        print(f"📹 Độ phân giải: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"🎯 Detector: {detector_backend}")
    
    def analyze_frame(self, frame):
        """
        Phân tích cảm xúc từ frame
        
        Args:
            frame: Frame từ camera
            
        Returns:
            Dict chứa kết quả phân tích
        """
        try:
            # Lưu frame tạm thời
            temp_path = "temp_frame.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Phân tích cảm xúc
            result = self.emotion_system.analyze_emotion_from_image(temp_path)
            
            # Xóa file tạm
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result.get('success', False) and result.get('results'):
                results = result['results']
                if 'dominant_emotion' in results:
                    self.current_emotion = results['dominant_emotion']
                    if 'emotion' in results and self.current_emotion in results['emotion']:
                        self.emotion_confidence = results['emotion'][self.current_emotion]
                    self.face_detected = True
                else:
                    self.face_detected = False
            else:
                self.face_detected = False
            
            return result
            
        except Exception as e:
            print(f"❌ Lỗi khi phân tích frame: {e}")
            self.face_detected = False
            return None
    
    def draw_emotion_info(self, frame):
        """
        Vẽ thông tin cảm xúc lên frame
        
        Args:
            frame: Frame cần vẽ thông tin
        """
        # Tính FPS
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.fps = self.frame_count / elapsed_time
        
        # Vẽ background cho thông tin
        info_height = 120
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], info_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Thông tin cơ bản
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, f"Detector: {self.detector_backend}", (10, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Thông tin cảm xúc
        if self.face_detected:
            emotion_color = self.emotion_colors.get(self.current_emotion, (255, 255, 255))
            emoji = self.emotion_emojis.get(self.current_emotion, '😐')
            
            # Vẽ cảm xúc chính
            emotion_text = f"Emotion: {emoji} {self.current_emotion.upper()}"
            cv2.putText(frame, emotion_text, (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, emotion_color, 2)
            
            # Vẽ độ tin cậy
            confidence_text = f"Confidence: {self.emotion_confidence:.2f}"
            cv2.putText(frame, confidence_text, (10, 105), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "No face detected", (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Vẽ hướng dẫn
        cv2.putText(frame, "Press 'q' to quit, 's' to save frame", (frame.shape[1] - 350, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def save_frame(self, frame):
        """
        Lưu frame hiện tại
        
        Args:
            frame: Frame cần lưu
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"camera_frame_{timestamp}.jpg"
        
        # Tạo thư mục nếu chưa có
        os.makedirs("camera_captures", exist_ok=True)
        filepath = os.path.join("camera_captures", filename)
        
        cv2.imwrite(filepath, frame)
        print(f"📸 Đã lưu frame: {filepath}")
        
        # Phân tích và lưu kết quả
        if self.face_detected:
            result = {
                "image_path": filepath,
                "analysis_time": datetime.now().isoformat(),
                "emotion": self.current_emotion,
                "confidence": self.emotion_confidence,
                "detector": self.detector_backend
            }
            
            result_file = filepath.replace(".jpg", "_result.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"📄 Đã lưu kết quả: {result_file}")
    
    def run(self, analysis_interval=30):
        """
        Chạy ứng dụng camera real-time
        
        Args:
            analysis_interval: Số frame giữa các lần phân tích (mặc định: 30)
        """
        print("🎥 Bắt đầu nhận diện cảm xúc real-time...")
        print("💡 Hướng dẫn:")
        print("   - Nhấn 'q' để thoát")
        print("   - Nhấn 's' để lưu frame hiện tại")
        print("   - Nhấn 'a' để phân tích ngay lập tức")
        print("   - Nhấn 'd' để thay đổi detector")
        
        frame_counter = 0
        
        try:
            while True:
                # Đọc frame từ camera
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Không thể đọc frame từ camera")
                    break
                
                # Phân tích cảm xúc theo interval
                frame_counter += 1
                if frame_counter % analysis_interval == 0:
                    self.analyze_frame(frame)
                
                # Vẽ thông tin lên frame
                self.draw_emotion_info(frame)
                
                # Hiển thị frame
                cv2.imshow('Real-time Emotion Detection', frame)
                
                # Xử lý phím nhấn
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("👋 Thoát ứng dụng...")
                    break
                elif key == ord('s'):
                    self.save_frame(frame)
                elif key == ord('a'):
                    print("🔍 Phân tích ngay lập tức...")
                    self.analyze_frame(frame)
                elif key == ord('d'):
                    self.change_detector()
        
        except KeyboardInterrupt:
            print("\n👋 Thoát ứng dụng...")
        finally:
            self.cleanup()
    
    def change_detector(self):
        """
        Thay đổi detector backend
        """
        detectors = ["opencv", "mtcnn", "retinaface", "mediapipe"]
        current_index = detectors.index(self.detector_backend)
        next_index = (current_index + 1) % len(detectors)
        new_detector = detectors[next_index]
        
        print(f"🔄 Thay đổi detector từ {self.detector_backend} sang {new_detector}")
        self.detector_backend = new_detector
        self.emotion_system = EmotionDetectionSystem(detector_backend=new_detector)
    
    def cleanup(self):
        """
        Dọn dẹp tài nguyên
        """
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("🧹 Đã dọn dẹp tài nguyên")

def main():
    """
    Hàm chính
    """
    print("🎭 Camera Real-time Emotion Detection")
    print("=" * 50)
    
    # Kiểm tra camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Không thể mở camera. Vui lòng kiểm tra:")
        print("   - Camera có được kết nối không?")
        print("   - Camera có đang được sử dụng bởi ứng dụng khác không?")
        print("   - Quyền truy cập camera có được cấp không?")
        return
    cap.release()
    
    try:
        # Khởi tạo hệ thống
        emotion_camera = RealTimeEmotionDetection(camera_index=0, detector_backend="opencv")
        
        # Chạy ứng dụng
        emotion_camera.run(analysis_interval=30)  # Phân tích mỗi 30 frame
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("💡 Gợi ý:")
        print("   - Kiểm tra camera có hoạt động không")
        print("   - Thử thay đổi camera_index (0, 1, 2...)")
        print("   - Kiểm tra quyền truy cập camera")

if __name__ == "__main__":
    main() 