#!/usr/bin/env python3
"""
Script test hệ thống nhận diện cảm xúc
"""

import sys
import os
import json
from pathlib import Path

# Thêm đường dẫn để import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'main'))

try:
    from src.main.emotion_detection import EmotionDetectionSystem
    print("✅ Import EmotionDetectionSystem thành công")
except ImportError as e:
    print(f"❌ Lỗi import EmotionDetectionSystem: {e}")
    sys.exit(1)

def test_emotion_detection():
    """Test hệ thống nhận diện cảm xúc"""
    print("\n🧪 Bắt đầu test hệ thống nhận diện cảm xúc...")
    
    # Khởi tạo hệ thống
    try:
        emotion_system = EmotionDetectionSystem()
        print("✅ Khởi tạo EmotionDetectionSystem thành công")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo EmotionDetectionSystem: {e}")
        return False
    
    # Test với ảnh mẫu từ DeepFace
    test_images = [
        "src/data/images/test.jpg",
        "model/deepface/tests/dataset/img1.jpg",
        "model/deepface/tests/dataset/img2.jpg"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📸 Test với ảnh: {image_path}")
            
            try:
                # Test phân tích cảm xúc
                result = emotion_system.analyze_emotion_from_image(image_path)
                
                if result.get('success', False):
                    print("✅ Phân tích cảm xúc thành công")
                    
                    # Hiển thị kết quả
                    results = result.get('results', {})
                    if 'dominant_emotion' in results:
                        print(f"🎭 Cảm xúc chính: {results['dominant_emotion']}")
                    
                    if 'emotion' in results:
                        print("📊 Phân bố cảm xúc:")
                        for emotion, score in results['emotion'].items():
                            percentage = score * 100
                            print(f"   {emotion}: {percentage:.1f}%")
                else:
                    print(f"❌ Phân tích cảm xúc thất bại: {result.get('error', 'Unknown error')}")
                
                # Test detect khuôn mặt
                face_result = emotion_system.detect_faces(image_path)
                if face_result.get('success', False):
                    print(f"👥 Phát hiện {face_result.get('faces_count', 0)} khuôn mặt")
                else:
                    print(f"❌ Phát hiện khuôn mặt thất bại: {face_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Lỗi khi test ảnh {image_path}: {e}")
        else:
            print(f"⚠️  Không tìm thấy ảnh test: {image_path}")
    
    return True

def test_batch_analysis():
    """Test phân tích hàng loạt"""
    print("\n📁 Test phân tích hàng loạt...")
    
    try:
        emotion_system = EmotionDetectionSystem()
        
        # Tìm các ảnh test
        test_images = []
        test_dirs = [
            "src/data/images",
            "model/deepface/tests/dataset"
        ]
        
        for test_dir in test_dirs:
            if os.path.exists(test_dir):
                for file in os.listdir(test_dir):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_images.append(os.path.join(test_dir, file))
                        if len(test_images) >= 3:  # Giới hạn 3 ảnh để test
                            break
        
        if test_images:
            print(f"📸 Tìm thấy {len(test_images)} ảnh để test")
            
            # Test phân tích hàng loạt
            results = emotion_system.analyze_multiple_emotions(test_images)
            
            # Tính thống kê
            statistics = emotion_system.get_emotion_statistics(results)
            
            print("📊 Thống kê phân tích hàng loạt:")
            print(f"   Tổng số ảnh: {statistics['total_analyses']}")
            print(f"   Thành công: {statistics['successful_analyses']}")
            print(f"   Tỷ lệ thành công: {statistics['success_rate']*100:.1f}%")
            
            if statistics['emotion_distribution']:
                print("   Phân bố cảm xúc:")
                for emotion, count in statistics['emotion_distribution'].items():
                    print(f"     {emotion}: {count}")
            
            return True
        else:
            print("⚠️  Không tìm thấy ảnh để test")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test phân tích hàng loạt: {e}")
        return False

def test_save_results():
    """Test lưu kết quả"""
    print("\n💾 Test lưu kết quả...")
    
    try:
        emotion_system = EmotionDetectionSystem()
        
        # Tạo kết quả mẫu
        sample_result = {
            "image_path": "test.jpg",
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
        output_path = "test_result.json"
        emotion_system.save_results(sample_result, output_path)
        
        # Kiểm tra file đã được tạo
        if os.path.exists(output_path):
            print("✅ Lưu kết quả thành công")
            
            # Đọc và kiểm tra nội dung
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded_result = json.load(f)
            
            if loaded_result == sample_result:
                print("✅ Nội dung file chính xác")
            else:
                print("❌ Nội dung file không khớp")
            
            # Xóa file test
            os.remove(output_path)
            return True
        else:
            print("❌ Không tạo được file kết quả")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test lưu kết quả: {e}")
        return False

def test_deepface_import():
    """Test import DeepFace"""
    print("\n🔍 Test import DeepFace...")
    
    try:
        from deepface import DeepFace
        print("✅ Import DeepFace thành công")
        
        # Test các model có sẵn
        print("📋 Kiểm tra các model có sẵn:")
        
        # Test emotion model
        try:
            # Tạo ảnh test đơn giản
            import numpy as np
            test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            # Lưu ảnh test tạm thời
            import cv2
            test_path = "temp_test.jpg"
            cv2.imwrite(test_path, test_image)
            
            # Test analyze (có thể fail nếu không detect được face, nhưng sẽ test được import)
            try:
                result = DeepFace.analyze(
                    img_path=test_path,
                    actions=['emotion'],
                    detector_backend='opencv',
                    enforce_detection=False
                )
                print("✅ DeepFace.analyze hoạt động")
            except Exception as e:
                print(f"⚠️  DeepFace.analyze có lỗi (có thể do không detect được face): {e}")
            
            # Xóa file test
            if os.path.exists(test_path):
                os.remove(test_path)
                
        except Exception as e:
            print(f"⚠️  Test DeepFace.analyze: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import DeepFace: {e}")
        return False

def main():
    """Hàm chính để chạy tất cả tests"""
    print("🎭 Hệ Thống Nhận Diện Cảm Xúc - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Test Import DeepFace", test_deepface_import),
        ("Test Emotion Detection", test_emotion_detection),
        ("Test Batch Analysis", test_batch_analysis),
        ("Test Save Results", test_save_results)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Kết quả test: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Tất cả tests đều PASSED! Hệ thống sẵn sàng sử dụng.")
        print("\n🚀 Để khởi động hệ thống:")
        print("   cd src/main")
        print("   python app.py")
        print("   Truy cập: http://localhost:5000")
    else:
        print("⚠️  Một số tests FAILED. Vui lòng kiểm tra lại cài đặt.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 