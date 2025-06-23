#!/usr/bin/env python3
"""
Demo hệ thống nhận diện cảm xúc
"""

import sys
import os
import json
from pathlib import Path

# Thêm đường dẫn để import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'main'))

try:
    from emotion_detection import EmotionDetectionSystem
    print("✅ Import EmotionDetectionSystem thành công")
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    print("Vui lòng chạy: python start_system.py")
    sys.exit(1)

def demo_single_analysis():
    """Demo phân tích đơn lẻ"""
    print("\n🎭 Demo: Phân tích cảm xúc đơn lẻ")
    print("-" * 40)
    
    # Khởi tạo hệ thống
    emotion_system = EmotionDetectionSystem()
    
    # Tìm ảnh test
    test_images = [
        "model/deepface/tests/dataset/img1.jpg",
        "model/deepface/tests/dataset/img2.jpg",
        "model/deepface/tests/dataset/img3.jpg"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📸 Phân tích ảnh: {image_path}")
            
            try:
                # Phân tích cảm xúc
                result = emotion_system.analyze_emotion_from_image(image_path)
                
                if result.get('success', False):
                    results = result.get('results', {})
                    
                    # Hiển thị cảm xúc chính
                    if 'dominant_emotion' in results:
                        emotion = results['dominant_emotion']
                        emoji_map = {
                            'angry': '😠',
                            'disgust': '🤢', 
                            'fear': '😨',
                            'happy': '😊',
                            'sad': '😢',
                            'surprise': '😲',
                            'neutral': '😐'
                        }
                        emoji = emoji_map.get(emotion, '😐')
                        print(f"🎭 Cảm xúc chính: {emoji} {emotion.upper()}")
                    
                    # Hiển thị phân bố cảm xúc
                    if 'emotion' in results:
                        print("📊 Phân bố cảm xúc:")
                        emotions = results['emotion']
                        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                        
                        for emotion, score in sorted_emotions:
                            percentage = score * 100
                            bar_length = int(percentage / 5)  # 5% = 1 ký tự
                            bar = "█" * bar_length
                            print(f"   {emotion:10}: {bar} {percentage:5.1f}%")
                    
                    # Detect khuôn mặt
                    face_result = emotion_system.detect_faces(image_path)
                    if face_result.get('success', False):
                        faces_count = face_result.get('faces_count', 0)
                        print(f"👥 Phát hiện {faces_count} khuôn mặt")
                    
                else:
                    print(f"❌ Lỗi: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Lỗi khi phân tích: {e}")
            
            break  # Chỉ demo với ảnh đầu tiên tìm thấy
        else:
            print(f"⚠️  Không tìm thấy ảnh: {image_path}")
    
    if not any(os.path.exists(img) for img in test_images):
        print("⚠️  Không tìm thấy ảnh test nào")
        print("Vui lòng thêm ảnh vào thư mục model/deepface/tests/dataset/")

def demo_batch_analysis():
    """Demo phân tích hàng loạt"""
    print("\n📁 Demo: Phân tích hàng loạt")
    print("-" * 40)
    
    emotion_system = EmotionDetectionSystem()
    
    # Tìm nhiều ảnh test
    test_dir = "model/deepface/tests/dataset"
    if os.path.exists(test_dir):
        image_files = []
        for file in os.listdir(test_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(os.path.join(test_dir, file))
                if len(image_files) >= 5:  # Giới hạn 5 ảnh
                    break
        
        if image_files:
            print(f"📸 Tìm thấy {len(image_files)} ảnh để phân tích")
            
            # Phân tích hàng loạt
            results = emotion_system.analyze_multiple_emotions(image_files)
            
            # Tính thống kê
            statistics = emotion_system.get_emotion_statistics(results)
            
            print(f"\n📊 Thống kê:")
            print(f"   Tổng số ảnh: {statistics['total_analyses']}")
            print(f"   Thành công: {statistics['successful_analyses']}")
            print(f"   Tỷ lệ thành công: {statistics['success_rate']*100:.1f}%")
            
            if statistics['emotion_distribution']:
                print(f"\n🎭 Phân bố cảm xúc:")
                emotion_counts = statistics['emotion_distribution']
                total_successful = statistics['successful_analyses']
                
                for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_successful) * 100
                    emoji_map = {
                        'angry': '😠',
                        'disgust': '🤢', 
                        'fear': '😨',
                        'happy': '😊',
                        'sad': '😢',
                        'surprise': '😲',
                        'neutral': '😐'
                    }
                    emoji = emoji_map.get(emotion, '😐')
                    print(f"   {emoji} {emotion:10}: {count:2d} ảnh ({percentage:5.1f}%)")
        else:
            print("⚠️  Không tìm thấy ảnh trong thư mục test")
    else:
        print("⚠️  Không tìm thấy thư mục test")

def demo_save_results():
    """Demo lưu kết quả"""
    print("\n💾 Demo: Lưu kết quả")
    print("-" * 40)
    
    emotion_system = EmotionDetectionSystem()
    
    # Tạo kết quả mẫu
    sample_result = {
        "image_path": "demo.jpg",
        "analysis_time": "2024-01-01T12:00:00",
        "model_used": "emotion",
        "detector_used": "opencv",
        "success": True,
        "results": {
            "dominant_emotion": "happy",
            "emotion": {
                "angry": 0.01,
                "disgust": 0.02,
                "fear": 0.03,
                "happy": 0.85,
                "sad": 0.02,
                "surprise": 0.05,
                "neutral": 0.02
            }
        }
    }
    
    # Lưu kết quả
    output_path = "demo_result.json"
    emotion_system.save_results(sample_result, output_path)
    
    if os.path.exists(output_path):
        print(f"✅ Đã lưu kết quả vào: {output_path}")
        
        # Đọc và hiển thị nội dung
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_result = json.load(f)
        
        print(f"📄 Nội dung file:")
        print(json.dumps(loaded_result, indent=2, ensure_ascii=False))
        
        # Xóa file demo
        os.remove(output_path)
        print(f"🗑️  Đã xóa file demo: {output_path}")
    else:
        print("❌ Không thể lưu kết quả")

def main():
    """Hàm chính"""
    print("🎭 Demo Hệ Thống Nhận Diện Cảm Xúc")
    print("=" * 50)
    
    try:
        # Demo 1: Phân tích đơn lẻ
        demo_single_analysis()
        
        # Demo 2: Phân tích hàng loạt
        demo_batch_analysis()
        
        # Demo 3: Lưu kết quả
        demo_save_results()
        
        print("\n" + "=" * 50)
        print("🎉 Demo hoàn thành!")
        print("\n🚀 Để sử dụng web interface:")
        print("   python start_system.py")
        print("   Truy cập: http://localhost:5000")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo bị dừng")
    except Exception as e:
        print(f"\n❌ Lỗi trong demo: {e}")

if __name__ == "__main__":
    main() 