# Ứng dụng Nhận Diện Cảm Xúc Học Sinh Qua Webcam

## Mục đích
Ứng dụng giúp giáo viên theo dõi cảm xúc học sinh trong quá trình học online, hỗ trợ điều chỉnh phương pháp giảng dạy phù hợp.

## Tính năng chính
- Nhận diện cảm xúc khuôn mặt học sinh qua webcam (real-time, tự động mỗi 5 giây)
- Lưu lịch sử cảm xúc vào file CSV
- Thống kê cảm xúc bằng biểu đồ
- Giao diện web tiếng Việt, menu điều hướng thân thiện
- Xem lịch sử, thống kê, giới thiệu hệ thống

## Công nghệ sử dụng
- Python (Flask, OpenCV, DeepFace, numpy)
- HTML/CSS/JS (Chart.js cho biểu đồ)

## Hướng dẫn cài đặt và sử dụng

### 1. Cài đặt thư viện
```bash
pip install flask opencv-python deepface numpy
```

### 2. Chạy ứng dụng
```bash
cd src
python app.py
```

### 3. Truy cập giao diện web
Mở trình duyệt và vào [http://localhost:5000](http://localhost:5000)

### 4. Sử dụng
- Nhấn **Bật camera** để hệ thống tự động nhận diện cảm xúc liên tục
- Xem lịch sử tại menu **Lịch sử**
- Xem thống kê tại menu **Thống kê**
- Xem giới thiệu tại menu **Giới thiệu**

## Cấu trúc thư mục
```
BTL-TGMT/
├── dataset/                # Ảnh mẫu (nếu muốn mở rộng training)
├── model/                  # Thư viện DeepFace
├── src/
│   ├── app.py              # Flask backend
│   ├── emotion_recognition.py # Xử lý nhận diện cảm xúc
│   ├── templates/
│   │   ├── index.html      # Giao diện nhận diện
│   │   ├── history.html    # Giao diện lịch sử
│   │   ├── stats.html      # Giao diện thống kê
│   │   ├── about.html      # Trang giới thiệu
│   │   └── navbar.html     # Menu điều hướng
│   └── static/
│       ├── js/camera.js    # Xử lý webcam và gửi ảnh
│       └── css/style.css   # Giao diện
└── README.md
```

## Đề xuất mở rộng
- Nhận diện nhiều khuôn mặt cùng lúc
- Lưu lịch sử vào database (SQLite, MySQL, ...)
- Thêm xác thực người dùng, phân quyền giáo viên/học sinh
- Thêm cảnh báo tự động khi học sinh có cảm xúc tiêu cực kéo dài
- Làm đẹp giao diện với Bootstrap/Material UI

---
**Project dành cho học tập, nghiên cứu và phát triển ứng dụng AI trong giáo dục.** 