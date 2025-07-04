# 🎭 Hệ Thống Nhận Diện Cảm Xúc

Hệ thống nhận diện cảm xúc sử dụng AI và DeepFace để phân tích cảm xúc từ ảnh khuôn mặt.

## ✨ Tính Năng

- **Phân tích cảm xúc đơn lẻ**: Upload một ảnh để phân tích cảm xúc
- **Phân tích hàng loạt**: Upload nhiều ảnh cùng lúc để phân tích
- **Phát hiện khuôn mặt**: Detect và đếm số lượng khuôn mặt trong ảnh
- **Thống kê**: Xem thống kê tổng quan về các lần phân tích
- **Web Interface**: Giao diện web thân thiện với người dùng
- **API RESTful**: Cung cấp API để tích hợp với các ứng dụng khác

## 🚀 Cài Đặt

### Yêu cầu hệ thống
- Python 3.8+
- Windows/Linux/macOS

### Bước 1: Clone repository
```bash
git clone <repository-url>
cd BTL-TGMT
```

### Bước 2: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Cài đặt DeepFace (nếu chưa có)
```bash
cd model/deepface
pip install -e .
cd ../..
```

## 🎯 Sử Dụng

### Khởi động hệ thống
```bash
cd src/main
python app.py
```

Hệ thống sẽ chạy tại: `http://localhost:5000`

### Sử dụng Web Interface

1. **Phân tích đơn lẻ**:
   - Chọn tab "Phân Tích Đơn Lẻ"
   - Upload ảnh hoặc kéo thả file
   - Nhấn "Phân Tích Cảm Xúc"

2. **Phân tích hàng loạt**:
   - Chọn tab "Phân Tích Hàng Loạt"
   - Upload nhiều ảnh
   - Nhấn "Phân Tích Hàng Loạt"

3. **Phát hiện khuôn mặt**:
   - Chọn tab "Phát Hiện Khuôn Mặt"
   - Upload ảnh
   - Nhấn "Phát Hiện Khuôn Mặt"

4. **Xem thống kê**:
   - Chọn tab "Thống Kê"
   - Nhấn "Tải Thống Kê"

### Sử dụng API

#### Phân tích cảm xúc
```bash
curl -X POST -F "image=@path/to/image.jpg" http://localhost:5000/api/analyze
```

#### Phân tích hàng loạt
```bash
curl -X POST -F "images=@image1.jpg" -F "images=@image2.jpg" http://localhost:5000/api/batch-analyze
```

#### Phát hiện khuôn mặt
```bash
curl -X POST -F "image=@path/to/image.jpg" http://localhost:5000/api/detect-faces
```

#### Lấy thống kê
```bash
curl http://localhost:5000/api/statistics
```

## 📁 Cấu Trúc Dự Án

```
BTL-TGMT/
├── src/
│   ├── main/
│   │   ├── app.py                 # Flask web application
│   │   ├── emotion_detection.py   # Core emotion detection logic
│   │   └── templates/
│   │       └── index.html         # Web interface
│   └── data/
│       ├── images/                # Sample images
│       ├── uploads/               # Uploaded images
│       ├── results/               # Analysis results
│       └── emotions.csv           # Sample data
├── model/
│   └── deepface/                  # DeepFace library
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Cấu Hình

### Thay đổi cấu hình trong `app.py`:

```python
# Kích thước file tối đa (mặc định: 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Thư mục lưu file upload
app.config['UPLOAD_FOLDER'] = 'src/data/uploads'

# Thư mục lưu kết quả
app.config['RESULTS_FOLDER'] = 'src/data/results'
```

### Thay đổi model và detector trong `emotion_detection.py`:

```python
# Khởi tạo với model và detector khác
emotion_system = EmotionDetectionSystem(
    model_name="emotion",      # emotion, age, gender, race
    detector_backend="opencv"  # opencv, mtcnn, retinaface, mediapipe, yolo
)
```

## 📊 Kết Quả Phân Tích

Hệ thống có thể nhận diện 7 loại cảm xúc:
- 😠 **Angry** (Giận dữ)
- 🤢 **Disgust** (Ghê tởm)
- 😨 **Fear** (Sợ hãi)
- 😊 **Happy** (Vui vẻ)
- 😢 **Sad** (Buồn bã)
- 😲 **Surprise** (Ngạc nhiên)
- 😐 **Neutral** (Bình thường)

### Format kết quả JSON:
```json
{
  "image_path": "path/to/image.jpg",
  "analysis_time": "2024-01-01T12:00:00",
  "model_used": "emotion",
  "detector_used": "opencv",
  "success": true,
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
```

## 🛠️ Phát Triển

### Thêm tính năng mới:

1. **Thêm API endpoint** trong `app.py`:
```python
@app.route('/api/new-feature', methods=['POST'])
def new_feature():
    # Implementation here
    pass
```

2. **Thêm logic xử lý** trong `emotion_detection.py`:
```python
def new_analysis_method(self, image_path: str) -> Dict:
    # Implementation here
    pass
```

3. **Cập nhật web interface** trong `templates/index.html`

### Chạy tests:
```bash
# Tạo test script
python -m pytest tests/
```

## 🐛 Xử Lý Lỗi

### Lỗi thường gặp:

1. **"No face detected"**:
   - Đảm bảo ảnh có khuôn mặt rõ ràng
   - Thử detector khác (mtcnn, retinaface)

2. **"Model not found"**:
   - Chạy lại `pip install -e .` trong thư mục deepface
   - Kiểm tra kết nối internet để download model

3. **"File too large"**:
   - Giảm kích thước ảnh
   - Tăng `MAX_CONTENT_LENGTH` trong cấu hình

## 📈 Hiệu Suất

- **Thời gian xử lý**: ~2-5 giây/ảnh (tùy thuộc vào kích thước và độ phức tạp)
- **Độ chính xác**: ~85-95% (tùy thuộc vào chất lượng ảnh)
- **Hỗ trợ format**: JPG, PNG, GIF, BMP
- **Kích thước file**: Tối đa 16MB

## 📚 Hướng Dẫn Huấn Luyện Model

Chi tiết cách huấn luyện lại mô hình cảm xúc nằm trong tài liệu [TRAINING_GUIDE.md](TRAINING_GUIDE.md). Tài liệu cung cấp hướng dẫn chuẩn bị dữ liệu và sử dụng script `train_emotion_model.py` để fine-tune mô hình.

## 🤝 Đóng Góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📄 License

Dự án này được phát hành dưới MIT License.

## 📞 Liên Hệ

- Email: your.email@example.com
- GitHub: [your-username](https://github.com/your-username)

---

**Lưu ý**: Hệ thống này sử dụng DeepFace library và các model AI. Vui lòng tuân thủ các quy định về bản quyền và sử dụng hợp lý.
