# Hướng Dẫn Tối Ưu Hiệu Suất - Emotion Detection System

## Tổng Quan Các Cải Tiến

### 1. Tối Ưu Frontend (CSS & JavaScript)

#### CSS Optimizations:
- **GPU Acceleration**: Sử dụng `transform: translateZ(0)` và `will-change` để tối ưu rendering
- **Reduced Transitions**: Giảm thời gian transition từ 0.3s xuống 0.2s
- **Optimized Animations**: Sử dụng `ease-out` thay vì `ease-in-out` cho hiệu suất tốt hơn
- **Box-sizing**: Áp dụng `border-box` cho tất cả elements
- **Reduced Reflow**: Tối ưu layout để giảm reflow và repaint

#### JavaScript Optimizations:
- **Debouncing**: Ngăn chặn multiple API calls
- **Throttling**: Giới hạn real-time analysis (2s minimum interval)
- **Request Prevention**: Ngăn chặn multiple simultaneous requests
- **Memory Management**: Cleanup resources khi chuyển tab
- **Error Handling**: Xử lý lỗi tốt hơn với fallback mechanisms

### 2. Backend Optimizations

#### API Improvements:
- **Caching System**: Cache thống kê trong 5 phút
- **Parallel Processing**: Xử lý batch images song song
- **Memory Management**: Background cleanup thread
- **Image Preprocessing**: Resize ảnh lớn trước khi xử lý
- **Error Recovery**: Fallback mechanisms cho DeepFace failures

#### Performance Monitoring:
- **Resource Monitoring**: Theo dõi CPU, Memory, Disk usage
- **Performance Decorators**: Monitor execution time và memory usage
- **Automatic Cleanup**: Tự động cleanup khi resource usage cao

### 3. Database & File Management

#### File Handling:
- **Optimized File Validation**: Cache file existence checks
- **Efficient Storage**: Tối ưu file upload và storage
- **Cleanup Routines**: Tự động xóa temporary files

## Cách Sử Dụng

### 1. Khởi Động Hệ Thống

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Khởi động server
python src/main/app.py
```

### 2. Monitoring Performance

```python
from src.main.performance_optimizer import get_performance_stats

# Lấy thống kê hiệu suất
stats = get_performance_stats()
print(stats)
```

### 3. Manual Cleanup

```python
from src.main.performance_optimizer import cleanup_system

# Cleanup toàn bộ hệ thống
cleanup_system()
```

## Các Tính Năng Mới

### 1. Real-time Performance Monitoring
- Theo dõi CPU, Memory usage real-time
- Tự động cleanup khi resource usage cao
- Background monitoring thread

### 2. Enhanced Caching
- Cache thống kê trong 5 phút
- LRU cache cho image processing
- Intelligent cache invalidation

### 3. Improved Error Handling
- Fallback mechanisms cho DeepFace failures
- Better error messages và logging
- Graceful degradation

### 4. Memory Optimization
- Image preprocessing và resizing
- Automatic garbage collection
- Memory usage monitoring

## Troubleshooting

### 1. High Memory Usage
```python
# Kiểm tra memory usage
from src.main.performance_optimizer import performance_optimizer
stats = performance_optimizer.monitor_resources()
print(f"Memory usage: {stats['memory_percent']}%")

# Manual cleanup
performance_optimizer.cleanup_memory()
```

### 2. Slow Processing
- Kiểm tra image size (tự động resize nếu > 1024px)
- Monitor CPU usage
- Sử dụng parallel processing cho batch operations

### 3. Cache Issues
```python
from src.main.performance_optimizer import cache_manager

# Clear cache
cache_manager.clear()

# Check cache stats
stats = cache_manager.get_stats()
print(f"Cache usage: {stats['usage_percent']}%")
```

## Best Practices

### 1. Image Processing
- Sử dụng ảnh có kích thước hợp lý (< 1024px)
- Format: JPG, PNG, GIF, BMP
- Tối ưu ảnh trước khi upload

### 2. Batch Processing
- Không upload quá nhiều ảnh cùng lúc (max 10)
- Sử dụng batch processing cho nhiều ảnh
- Monitor progress và cancel nếu cần

### 3. Real-time Analysis
- Sử dụng throttling để tránh overwhelming server
- Monitor camera performance
- Stop analysis khi không cần thiết

## Performance Metrics

### Target Performance:
- **Response Time**: < 3s cho single image
- **Memory Usage**: < 80% system memory
- **CPU Usage**: < 90% system CPU
- **Cache Hit Rate**: > 80%

### Monitoring Commands:
```python
# Get comprehensive stats
from src.main.performance_optimizer import get_performance_stats
stats = get_performance_stats()

# Monitor specific metrics
print(f"Memory: {stats['resources']['resources']['memory_percent']}%")
print(f"CPU: {stats['resources']['resources']['cpu_percent']}%")
print(f"Cache: {stats['cache']['usage_percent']}%")
```

## Future Improvements

### 1. Planned Optimizations:
- WebSocket cho real-time updates
- Redis cache cho distributed systems
- GPU acceleration cho image processing
- Async processing với Celery

### 2. Monitoring Enhancements:
- Prometheus metrics
- Grafana dashboards
- Alert system cho performance issues
- Automated scaling

### 3. Code Optimizations:
- Cython cho critical paths
- JIT compilation
- Memory pooling
- Optimized data structures

## Support

Nếu gặp vấn đề về hiệu suất:
1. Kiểm tra system resources
2. Monitor performance stats
3. Clear cache và restart system
4. Contact development team

---

**Lưu ý**: Hệ thống đã được tối ưu để giảm lag và cải thiện hiệu suất. Nếu vẫn gặp vấn đề, hãy kiểm tra system requirements và network connectivity. 