#!/usr/bin/env python3
"""
Test script để kiểm tra JSON serialization
"""

import json
import numpy as np
from src.main.emotion_detection import make_json_serializable, EmotionDetectionSystem
import os

def test_json_serialization():
    """Test JSON serialization với numpy arrays"""
    
    print("Testing JSON serialization...")
    
    # Test với numpy arrays
    test_data = {
        'array': np.array([1, 2, 3, 4, 5]),
        'matrix': np.array([[1, 2], [3, 4]]),
        'float': np.float64(3.14),
        'int': np.int64(42),
        'nested': {
            'array': np.array([10, 20, 30]),
            'normal': 'string'
        },
        'list_of_arrays': [
            np.array([1, 2]),
            np.array([3, 4])
        ]
    }
    
    print("Original data:")
    print(test_data)
    print()
    
    # Convert to JSON serializable
    serializable_data = make_json_serializable(test_data)
    
    print("Serializable data:")
    print(serializable_data)
    print()
    
    # Test JSON serialization
    try:
        json_string = json.dumps(serializable_data, indent=2)
        print("JSON serialization successful!")
        print("JSON output:")
        print(json_string)
        return True
    except Exception as e:
        print(f"JSON serialization failed: {e}")
        return False

def test_face_detection():
    """Test face detection với JSON serialization"""
    
    print("\nTesting face detection...")
    
    # Khởi tạo emotion system
    emotion_system = EmotionDetectionSystem()
    
    # Tìm ảnh test
    test_images = [
        "src/data/images/0/Happy.jpg",
        "src/data/images/1/Neutral.jpg",
        "src/data/uploads/test.jpg"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"Testing with image: {image_path}")
            
            try:
                # Detect faces
                result = emotion_system.detect_faces(image_path)
                
                print(f"Detection result: {result['success']}")
                print(f"Faces count: {result['faces_count']}")
                
                # Test JSON serialization
                try:
                    json_string = json.dumps(result, indent=2)
                    print("✅ Face detection result is JSON serializable!")
                    return True
                except Exception as e:
                    print(f"❌ JSON serialization failed: {e}")
                    return False
                    
            except Exception as e:
                print(f"❌ Face detection failed: {e}")
                continue
    
    print("❌ No test images found")
    return False

def test_emotion_analysis():
    """Test emotion analysis với JSON serialization"""
    
    print("\nTesting emotion analysis...")
    
    # Khởi tạo emotion system
    emotion_system = EmotionDetectionSystem()
    
    # Tìm ảnh test
    test_images = [
        "src/data/images/0/Happy.jpg",
        "src/data/images/1/Neutral.jpg",
        "src/data/uploads/test.jpg"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"Testing with image: {image_path}")
            
            try:
                # Analyze emotion
                result = emotion_system.analyze_emotion_from_image(image_path)
                
                print(f"Analysis result: {result['success']}")
                
                # Test JSON serialization
                try:
                    json_string = json.dumps(result, indent=2)
                    print("✅ Emotion analysis result is JSON serializable!")
                    return True
                except Exception as e:
                    print(f"❌ JSON serialization failed: {e}")
                    return False
                    
            except Exception as e:
                print(f"❌ Emotion analysis failed: {e}")
                continue
    
    print("❌ No test images found")
    return False

if __name__ == "__main__":
    print("=== JSON Serialization Test ===")
    
    # Test 1: Basic JSON serialization
    test1_passed = test_json_serialization()
    
    # Test 2: Face detection
    test2_passed = test_face_detection()
    
    # Test 3: Emotion analysis
    test3_passed = test_emotion_analysis()
    
    print("\n=== Test Results ===")
    print(f"Basic JSON serialization: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Face detection: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Emotion analysis: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 All tests passed! JSON serialization is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.") 