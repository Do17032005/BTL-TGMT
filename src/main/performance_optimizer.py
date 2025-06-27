"""
Performance Optimizer cho Emotion Detection System
Tối ưu hiệu suất và giảm lag cho web application
"""

import os
import gc
import psutil
import threading
import time
from typing import Dict, List, Optional
import logging
from functools import wraps
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Class tối ưu hiệu suất cho hệ thống
    """
    
    def __init__(self):
        self.memory_threshold = 80  # % memory usage threshold
        self.cpu_threshold = 90     # % CPU usage threshold
        self.cleanup_interval = 300  # seconds
        self.last_cleanup = time.time()
        
        # Start background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._background_cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def monitor_resources(self) -> Dict:
        """
        Monitor tài nguyên hệ thống
        """
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            return {
                'memory_percent': memory.percent,
                'memory_available': memory.available / (1024**3),  # GB
                'cpu_percent': cpu,
                'disk_percent': disk.percent,
                'disk_free': disk.free / (1024**3)  # GB
            }
        except Exception as e:
            logger.error(f"Lỗi khi monitor resources: {str(e)}")
            return {}
    
    def should_cleanup(self) -> bool:
        """
        Kiểm tra có cần cleanup không
        """
        resources = self.monitor_resources()
        current_time = time.time()
        
        # Cleanup nếu memory hoặc CPU quá cao
        if (resources.get('memory_percent', 0) > self.memory_threshold or 
            resources.get('cpu_percent', 0) > self.cpu_threshold):
            return True
        
        # Cleanup định kỳ
        if current_time - self.last_cleanup > self.cleanup_interval:
            return True
        
        return False
    
    def cleanup_memory(self):
        """
        Cleanup memory
        """
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear OpenCV cache
            cv2.destroyAllWindows()
            
            # Clear numpy caches (no direct API, force garbage collection)
            gc.collect()
            
            self.last_cleanup = time.time()
            logger.info("Memory cleanup completed")
            
        except Exception as e:
            logger.error(f"Lỗi khi cleanup memory: {str(e)}")
    
    def _background_cleanup(self):
        """
        Background cleanup thread
        """
        while True:
            try:
                time.sleep(60)  # Check every minute
                if self.should_cleanup():
                    self.cleanup_memory()
            except Exception as e:
                logger.error(f"Lỗi trong background cleanup: {str(e)}")
    
    def optimize_image(self, image: np.ndarray, max_size: int = 1024) -> np.ndarray:
        """
        Tối ưu ảnh để giảm memory usage
        """
        try:
            height, width = image.shape[:2]
            
            # Resize nếu ảnh quá lớn
            if max(height, width) > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert to uint8 nếu cần
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            
            return image
            
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu ảnh: {str(e)}")
            return image
    
    def get_optimization_stats(self) -> Dict:
        """
        Lấy thống kê tối ưu
        """
        resources = self.monitor_resources()
        return {
            'resources': resources,
            'last_cleanup': self.last_cleanup,
            'cleanup_interval': self.cleanup_interval,
            'memory_threshold': self.memory_threshold,
            'cpu_threshold': self.cpu_threshold
        }

def performance_monitor(func):
    """
    Decorator để monitor hiệu suất function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            
            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s, memory: {memory_used / 1024 / 1024:.2f}MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

def memory_efficient(func):
    """
    Decorator để tối ưu memory usage
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Cleanup trước khi thực thi
        gc.collect()
        
        result = func(*args, **kwargs)
        
        # Cleanup sau khi thực thi
        gc.collect()
        
        return result
    
    return wrapper

class ImageProcessor:
    """
    Class xử lý ảnh với tối ưu hiệu suất
    """
    
    def __init__(self, max_size: int = 1024):
        self.max_size = max_size
        self.optimizer = PerformanceOptimizer()
    
    @performance_monitor
    def process_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Xử lý ảnh với tối ưu hiệu suất
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Tối ưu ảnh
            optimized_image = self.optimizer.optimize_image(image, self.max_size)
            
            return optimized_image
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý ảnh {image_path}: {str(e)}")
            return None
    
    @memory_efficient
    def batch_process(self, image_paths: List[str]) -> List[Optional[np.ndarray]]:
        """
        Xử lý nhiều ảnh với tối ưu memory
        """
        results = []
        
        for image_path in image_paths:
            result = self.process_image(image_path)
            results.append(result)
            
            # Cleanup sau mỗi ảnh
            if self.optimizer.should_cleanup():
                self.optimizer.cleanup_memory()
        
        return results

class CacheManager:
    """
    Quản lý cache để tối ưu hiệu suất
    """
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = {}
        self.access_times = {}
        self.lock = threading.Lock()
    
    def get(self, key: str):
        """
        Lấy giá trị từ cache
        """
        with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]
            return None
    
    def set(self, key: str, value):
        """
        Đặt giá trị vào cache
        """
        with self.lock:
            # Evict least recently used nếu cache đầy
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def _evict_lru(self):
        """
        Xóa item ít được sử dụng nhất
        """
        if not self.access_times:
            return
        
        lru_key = min(self.access_times, key=self.access_times.get)
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def clear(self):
        """
        Xóa toàn bộ cache
        """
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
    
    def get_stats(self) -> Dict:
        """
        Lấy thống kê cache
        """
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'usage_percent': len(self.cache) / self.max_size * 100
            }

# Global instances
performance_optimizer = PerformanceOptimizer()
image_processor = ImageProcessor()
cache_manager = CacheManager()

def get_performance_stats() -> Dict:
    """
    Lấy thống kê hiệu suất tổng hợp
    """
    return {
        'resources': performance_optimizer.get_optimization_stats(),
        'cache': cache_manager.get_stats(),
        'timestamp': time.time()
    }

def cleanup_system():
    """
    Cleanup toàn bộ hệ thống
    """
    performance_optimizer.cleanup_memory()
    cache_manager.clear()
    logger.info("System cleanup completed")

if __name__ == "__main__":
    # Test performance optimizer
    print("Testing Performance Optimizer...")
    
    # Monitor resources
    stats = get_performance_stats()
    print(f"Performance Stats: {stats}")
    
    # Test image processing
    test_image_path = "test_image.jpg"
    if os.path.exists(test_image_path):
        processed_image = image_processor.process_image(test_image_path)
        print(f"Image processed: {processed_image is not None}")
    
    print("Performance Optimizer test completed") 