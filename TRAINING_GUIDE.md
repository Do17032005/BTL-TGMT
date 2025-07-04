# Hướng Dẫn Huấn Luyện Mô Hình Nhận Diện Cảm Xúc

Tài liệu này hướng dẫn cách huấn luyện lại mô hình nhận diện cảm xúc dựa trên thư viện **DeepFace**.

## 1. Chuẩn Bị Dữ Liệu

- Tạo một thư mục chứa ảnh theo cấu trúc:
```
<dataset>/
├── angry/
├── disgust/
├── fear/
├── happy/
├── sad/
├── surprise/
└── neutral/
```
- Mỗi thư mục con chứa các ảnh thuộc lớp cảm xúc tương ứng.
- Nên sử dụng tối thiểu vài nghìn ảnh cho mỗi lớp để đạt kết quả tốt.

## 2. Cài Đặt Phụ Thuộc

```bash
pip install -r requirements.txt
```

Thư viện `tensorflow` không nằm trong `requirements.txt`. Nếu môi trường của bạn chưa có, hãy cài thêm:
```bash
pip install tensorflow
```

## 3. Huấn Luyện

Sử dụng script `src/train/train_emotion_model.py`:
```bash
python src/train/train_emotion_model.py <path_to_dataset> --output my_emotion_model.h5 --epochs 30 --batch 32
```
Trong đó:
- `<path_to_dataset>`: Đường dẫn đến thư mục dữ liệu.
- `--output`: Tên file model sau khi huấn luyện (mặc định `emotion_model.h5`).
- `--epochs`: Số epoch (mặc định 30).
- `--batch`: Kích thước batch (mặc định 32).

Script sử dụng mô hình **MobileNetV2** pre-trained để fine-tune cho bài toán nhận diện cảm xúc. Kết quả model `.h5` có thể dùng với DeepFace thông qua tham số `model_name` trong `EmotionDetectionSystem`.

## 4. Sử Dụng Model Đã Huấn Luyện

Sau khi huấn luyện xong, cập nhật `EmotionDetectionSystem` để sử dụng model mới:
```python
emotion_system = EmotionDetectionSystem(model_name="/path/to/my_emotion_model.h5", detector_backend="opencv")
```
Đảm bảo đường dẫn tới file model là chính xác. Khi chạy hệ thống, DeepFace sẽ tải model tùy chỉnh này và thực hiện phân tích cảm xúc dựa trên dữ liệu bạn đã huấn luyện.
