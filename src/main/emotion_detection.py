import os
import cv2
import numpy as np
from deepface import DeepFace
from typing import Dict, List, Tuple, Optional, Union, Any
import json
from datetime import datetime
import logging
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_json_serializable(obj: Any) -> Any:
    """
    Convert object to JSON serializable format
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(make_json_serializable(item) for item in obj)
    else:
        return obj

class EmotionDetectionSystem:
    """
    Hệ thống nhận diện cảm xúc sử dụng DeepFace với tối ưu hiệu suất
    """
    
    def __init__(self, model_name: str = "emotion", detector_backend: str = "opencv"):
        """
        Khởi tạo hệ thống nhận diện cảm xúc
        
        Args:
            model_name: Tên model để nhận diện cảm xúc (emotion, age, gender, race)
            detector_backend: Backend để detect khuôn mặt (opencv, mtcnn, retinaface, etc.)
        """
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.supported_models = ["emotion", "age", "gender", "race"]
        self.supported_detectors = ["opencv", "mtcnn", "retinaface", "mediapipe", "yolo"]
        
        # Thread pool cho xử lý đa luồng
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache cho model loading
        self._model_cache = {}
        self._cache_lock = threading.Lock()
        
        logger.info(f"Khởi tạo EmotionDetectionSystem với model: {model_name}, detector: {detector_backend}")
    
    def __del__(self):
        """Cleanup khi object bị destroy"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
    
    @lru_cache(maxsize=128)
    def _validate_image_path(self, image_path: str) -> bool:
        """
        Validate đường dẫn ảnh với cache
        """
        return os.path.exists(image_path) and os.path.isfile(image_path)
    
    def _preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Tiền xử lý ảnh để tối ưu hiệu suất
        """
        try:
            # Đọc ảnh với OpenCV
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Resize ảnh nếu quá lớn để tăng tốc độ xử lý
            height, width = image.shape[:2]
            max_size = 1024
            
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            return image
            
        except Exception as e:
            logger.error(f"Lỗi khi tiền xử lý ảnh {image_path}: {str(e)}")
            return None
    
    def analyze_emotion_from_image(self, image_path: str) -> Dict:
        """
        Phân tích cảm xúc từ ảnh với tối ưu hiệu suất
        
        Args:
            image_path: Đường dẫn đến ảnh
            
        Returns:
            Dict chứa kết quả phân tích
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Đang phân tích cảm xúc từ ảnh: {image_path}")
            
            # Kiểm tra file tồn tại với cache
            if not self._validate_image_path(image_path):
                raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
            
            # Tiền xử lý ảnh
            processed_image = self._preprocess_image(image_path)
            if processed_image is None:
                raise ValueError("Không thể đọc hoặc xử lý ảnh")
            
            # Phân tích cảm xúc sử dụng DeepFace với timeout
            try:
                result = DeepFace.analyze(
                    img_path=image_path,
                    actions=[self.model_name],
                    detector_backend=self.detector_backend,
                    enforce_detection=False
                )
            except Exception as deepface_error:
                # Fallback: thử với ảnh đã xử lý
                logger.warning(
                    f"DeepFace analyze failed, trying with processed image: {str(deepface_error)}"
                )
                result = DeepFace.analyze(
                    img_path=processed_image,
                    actions=[self.model_name],
                    detector_backend=self.detector_backend,
                    enforce_detection=False
                )
            
            # Xử lý kết quả
            if isinstance(result, list):
                result = result[0]  # Lấy kết quả đầu tiên nếu có nhiều khuôn mặt
            
            # Tính thời gian xử lý
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Thêm thông tin metadata
            analysis_result = {
                "image_path": image_path,
                "analysis_time": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "model_used": self.model_name,
                "detector_used": self.detector_backend,
                "success": True,
                "results": result
            }
            
            logger.info(f"Phân tích thành công trong {processing_time:.2f}s: {analysis_result}")
            return analysis_result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Lỗi khi phân tích cảm xúc sau {processing_time:.2f}s: {str(e)}")
            return {
                "image_path": image_path,
                "analysis_time": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "model_used": self.model_name,
                "detector_used": self.detector_backend,
                "success": False,
                "error": str(e),
                "results": None
            }
    
    def analyze_multiple_emotions_parallel(self, image_paths: List[str], max_workers: int = 4) -> List[Dict]:
        """
        Phân tích cảm xúc từ nhiều ảnh song song
        
        Args:
            image_paths: Danh sách đường dẫn ảnh
            max_workers: Số worker tối đa
            
        Returns:
            List các kết quả phân tích
        """
        results = []
        
        # Sử dụng ThreadPoolExecutor để xử lý song song
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit tất cả tasks
            future_to_path = {
                executor.submit(self.analyze_emotion_from_image, path): path 
                for path in image_paths
            }
            
            # Thu thập kết quả
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý ảnh {path}: {str(e)}")
                    results.append({
                        "image_path": path,
                        "success": False,
                        "error": str(e),
                        "results": None
                    })
        
        return results
    
    def analyze_multiple_emotions(self, image_paths: List[str]) -> List[Dict]:
        """
        Phân tích cảm xúc từ nhiều ảnh (backward compatibility)
        """
        return self.analyze_multiple_emotions_parallel(image_paths)
    
    def detect_faces(self, image_path: str) -> Dict:
        """
        Detect khuôn mặt trong ảnh với tối ưu hiệu suất
        
        Args:
            image_path: Đường dẫn đến ảnh
            
        Returns:
            Dict chứa thông tin về các khuôn mặt được detect
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Đang detect khuôn mặt từ ảnh: {image_path}")
            
            # Kiểm tra file tồn tại
            if not self._validate_image_path(image_path):
                raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
            
            # Detect khuôn mặt với timeout
            try:
                faces = DeepFace.extract_faces(
                    img_path=image_path,
                    detector_backend=self.detector_backend,
                    enforce_detection=False
                )
            except Exception as deepface_error:
                # Fallback với ảnh đã xử lý
                logger.warning(f"DeepFace extract_faces failed, trying with processed image: {str(deepface_error)}")
                processed_image = self._preprocess_image(image_path)
                if processed_image is None:
                    raise ValueError("Không thể đọc hoặc xử lý ảnh")

                faces = DeepFace.extract_faces(
                    img_path=processed_image,
                    detector_backend=self.detector_backend,
                    enforce_detection=False
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Convert numpy arrays to lists for JSON serialization
            serializable_faces = make_json_serializable(faces)
            
            result = {
                "image_path": image_path,
                "detection_time": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "detector_used": self.detector_backend,
                "success": True,
                "faces_count": len(faces),
                "faces": serializable_faces
            }
            
            logger.info(f"Detect thành công {len(faces)} khuôn mặt trong {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Lỗi khi detect khuôn mặt sau {processing_time:.2f}s: {str(e)}")
            return {
                "image_path": image_path,
                "detection_time": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "detector_used": self.detector_backend,
                "success": False,
                "error": str(e),
                "faces_count": 0,
                "faces": []
            }
    
    def get_emotion_statistics(self, results: List[Dict]) -> Dict:
        """
        Tính toán thống kê cảm xúc từ nhiều kết quả với tối ưu
        
        Args:
            results: Danh sách kết quả phân tích
            
        Returns:
            Dict chứa thống kê
        """
        emotion_counts = {}
        total_analyses = 0
        successful_analyses = 0
        total_processing_time = 0.0
        
        for result in results:
            total_analyses += 1
            if result.get("success", False) and result.get("results"):
                successful_analyses += 1
                
                # Cộng thời gian xử lý
                processing_time = result.get("processing_time_seconds", 0)
                total_processing_time += processing_time
                
                # Đếm cảm xúc
                if "dominant_emotion" in result["results"]:
                    emotion = result["results"]["dominant_emotion"]
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        avg_processing_time = total_processing_time / successful_analyses if successful_analyses > 0 else 0
        
        return {
            "total_analyses": total_analyses,
            "successful_analyses": successful_analyses,
            "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
            "average_processing_time": avg_processing_time,
            "total_processing_time": total_processing_time,
            "emotion_distribution": emotion_counts
        }
    
    def save_results(self, results: Union[Dict, List[Dict]], output_path: str):
        """
        Lưu kết quả vào file JSON với tối ưu
        
        Args:
            results: Kết quả phân tích
            output_path: Đường dẫn file output
        """
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert to JSON serializable format
            serializable_results = make_json_serializable(results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            logger.info(f"Đã lưu kết quả vào: {output_path}")
        except Exception as e:
            logger.error(f"Lỗi khi lưu kết quả: {str(e)}")
    
    def get_system_info(self) -> Dict:
        """
        Lấy thông tin hệ thống
        """
        return {
            "model_name": self.model_name,
            "detector_backend": self.detector_backend,
            "supported_models": self.supported_models,
            "supported_detectors": self.supported_detectors,
            "max_workers": self.executor._max_workers if hasattr(self.executor, '_max_workers') else 4
        }

# Hàm tiện ích để test
def test_emotion_detection():
    """
    Hàm test hệ thống nhận diện cảm xúc
    """
    # Khởi tạo hệ thống
    emotion_system = EmotionDetectionSystem()
    
    # Test với ảnh mẫu
    test_image_path = "test_image.jpg"
    
    if os.path.exists(test_image_path):
        print("Testing emotion detection...")
        result = emotion_system.analyze_emotion_from_image(test_image_path)
        print(f"Result: {result}")
    else:
        print(f"Test image not found: {test_image_path}")

if __name__ == "__main__":
    test_emotion_detection() 