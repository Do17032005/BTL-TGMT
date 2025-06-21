from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
from emotion_detector import EmotionDetector
from face_recognizer import FaceRecognizer
from student_manager import StudentManager
import atexit

app = Flask(__name__)
detector = EmotionDetector()
student_manager = StudentManager()
face_recognizer = FaceRecognizer(student_manager)
cap = cv2.VideoCapture(0)

register_mode = False
register_info = {}

def gen_frames():
    global register_mode, register_info
    count = 0
    while True:
        success, frame = cap.read()
        if not success:
            break
        if register_mode:
            # Đăng ký khuôn mặt
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face_img = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
                if 'samples' not in register_info:
                    register_info['samples'] = []
                if count < 10:
                    register_info['samples'].append({'image': face_img.tolist()})
                    count += 1
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Sample {count}/10", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            if count >= 10:
                student_manager.add_student(register_info['student_id'], register_info['student_name'], register_info['samples'])
                student_manager.save_students()
                face_recognizer.train_model()
                register_mode = False
                register_info = {}
        else:
            frame = detector.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', show_video=False, show_register=False, message=None)

@app.route('/recognize')
def recognize():
    return render_template('index.html', show_video=True, show_register=False, message=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    global register_mode, register_info
    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        register_mode = True
        register_info = {'student_id': student_id, 'student_name': student_name}
        return render_template('index.html', show_video=True, show_register=False, message="Đang đăng ký khuôn mặt...")
    return render_template('index.html', show_video=False, show_register=True, message=None)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@atexit.register
def cleanup():
    cap.release()

if __name__ == '__main__':
    app.run(debug=True)