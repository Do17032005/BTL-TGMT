import cv2
import numpy as np

class FaceRecognizer:
    def __init__(self, student_manager):
        self.student_manager = student_manager
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.trained = False

    def train_model(self):
        faces = []
        labels = []
        for student in self.student_manager.get_all_students():
            for face_data in student['facial_data']:
                faces.append(np.array(face_data['image'], dtype=np.uint8))
                # Đảm bảo label là số nguyên
                labels.append(int(student['id']))
        if len(faces) < 2:
            print("Không đủ dữ liệu khuôn mặt để huấn luyện. Hãy thêm ít nhất 2 ảnh khuôn mặt vào dữ liệu học sinh!")
            return
        self.recognizer.train(faces, np.array(labels, dtype=np.int32))
        self.trained = True

    def recognize_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            label, confidence = self.recognizer.predict(face_roi)
            if confidence < 100:
                student = self.student_manager.get_student_by_id(label)
                if student:
                    cv2.putText(frame, student['name'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            else:
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        return frame

    def recognize_faces(self, frame):
        if not self.trained:
            print("Model chưa được huấn luyện. Không thể nhận diện khuôn mặt.")
            return []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        recognized_ids = []
        for (x, y, w, h) in faces:
            face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            label, confidence = self.recognizer.predict(face_roi)
            if confidence < 100:
                recognized_ids.append(label)
        return recognized_ids

    def save_recognition_data(self, student_id, emotion):
        # Implement saving recognition data logic here
        pass

    def register_face(self, student_id, student_name, student_manager, num_samples=10):
        cap = cv2.VideoCapture(0)
        count = 0
        print(f"Đưa khuôn mặt vào khung hình để đăng ký cho học sinh: {student_name} (ID: {student_id})")
        face_samples = []

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Không nhận được frame từ camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                count += 1
                face_samples.append({'image': face_img.tolist()})  # Lưu dưới dạng list để lưu json

                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Sample {count}/{num_samples}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            cv2.imshow('Register Face', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if count >= num_samples:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Lưu dữ liệu khuôn mặt vào student_manager
        if count > 0:
            student_manager.add_student(student_id, student_name, face_samples)
            student_manager.save_students()
            print(f"Đã lưu {count} ảnh khuôn mặt cho học sinh {student_name} (ID: {student_id})")
        else:
            print("Không thu thập được ảnh khuôn mặt nào.")
