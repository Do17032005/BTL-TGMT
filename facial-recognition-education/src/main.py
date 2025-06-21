import cv2
import numpy as np
from emotion_detector import EmotionDetector
from face_recognizer import FaceRecognizer
from student_manager import StudentManager

def main():
    # Initialize the emotion detector and face recognizer
    emotion_detector = EmotionDetector()
    student_manager = StudentManager()
    student_manager.load_students()
    face_recognizer = FaceRecognizer(student_manager)

    while True:
        print("\nChọn chức năng:")
        print("1. Đăng ký khuôn mặt mới")
        print("2. Nhận diện khuôn mặt & cảm xúc")
        print("0. Thoát")
        choice = input("Nhập lựa chọn (1/2/0): ").strip()

        if choice == "1":
            student_id = input("Nhập ID học sinh: ").strip()
            student_name = input("Nhập tên học sinh: ").strip()
            face_recognizer.register_face(student_id, student_name, student_manager, num_samples=10)
            print("Đăng ký xong! Đang huấn luyện lại mô hình...")
            face_recognizer.train_model()
            print("Huấn luyện xong.")
        elif choice == "2":
            # Train model trước khi nhận diện
            face_recognizer.train_model()

            # Set up the camera
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("Cannot open camera")
                continue

            print("Press 'q' to quit nhận diện")
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Cannot receive frame from camera")
                    break

                # Process the frame for emotion detection
                processed_frame = emotion_detector.process_frame(frame)

                # Recognize faces in the frame
                if face_recognizer.trained:
                    recognized_students = face_recognizer.recognize_faces(frame)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_recognizer.face_cascade.detectMultiScale(gray, 1.3, 5)
                    for idx, (x, y, w, h) in enumerate(faces):
                        face_roi_gray = gray[y:y+h, x:x+w]
                        # Bạn cần tự phát hiện eyes, smiles, brightness, contrast ở đây
                        eyes = []      # TODO: phát hiện mắt
                        smiles = []    # TODO: phát hiện nụ cười
                        brightness = np.mean(face_roi_gray)
                        contrast = np.std(face_roi_gray)
                        emotion = emotion_detector.detect_emotion(face_roi_gray, eyes, smiles, brightness, contrast)
                        student_id = recognized_students[idx] if idx < len(recognized_students) else "Unknown"
                        cv2.putText(processed_frame, f"ID: {student_id}, Emotion: {emotion}", 
                                    (10, 30 + 30 * idx), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                else:
                    cv2.putText(processed_frame, "Chua co du lieu khuon mat de nhan dien!", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Show the processed frame
                cv2.imshow('Emotion Detection and Face Recognition', processed_frame)

                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # Release the camera and close windows
            cap.release()
            cv2.destroyAllWindows()
        elif choice == "0":
            print("Đã thoát chương trình.")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main()