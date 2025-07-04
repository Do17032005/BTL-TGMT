import csv
from datetime import datetime
import os
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
from emotion_recognition import predict_emotion

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "emotion_history.csv")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True)
    if not data or 'image' not in data:
        return jsonify({'error': 'No image data received'}), 400
    img_data = data['image']
    # img_data là base64 string
    img_bytes = base64.b64decode(img_data.split(',')[1])
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    emotion = predict_emotion(img)

    # Lưu lịch sử vào file CSV
    with open(HISTORY_FILE, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), emotion])

    return jsonify({'emotion': emotion})

@app.route('/history')
def history():
    history_data = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, encoding='utf-8') as f:
            reader = csv.reader(f)
            history_data = list(reader)
    return render_template('history.html', history=history_data)

@app.route('/stats')
def stats():
    # Đọc dữ liệu lịch sử
    emotion_counts = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 1:
                    emotion = row[1]
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    return render_template('stats.html', emotion_counts=emotion_counts)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True) 