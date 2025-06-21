# Facial Recognition in Education

This project aims to enhance the existing emotion detection system into a facial recognition training system that can be applied in educational settings, such as online classes, to recognize students' emotions.

## Project Structure

```
facial-recognition-education
├── src
│   ├── main.py               # Entry point of the application
│   ├── emotion_detector.py    # Emotion detection functionality
│   ├── face_recognizer.py     # Face recognition functionality
│   ├── student_manager.py      # Management of student data
│   ├── utils.py               # Utility functions
│   └── data
│       ├── __init__.py        # Marks the data directory as a package
│       └── students.json       # Student data in JSON format
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd facial-recognition-education
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage Guidelines

1. **Run the application:**
   To start the application, execute the following command:
   ```
   python src/main.py
   ```

2. **Camera Access:**
   Ensure that your camera is accessible and not being used by other applications.

3. **Emotion Detection and Recognition:**
   The system will detect students' emotions and recognize their faces in real-time. It will log the detected emotions and recognized faces for further analysis.

## Overview of Functionality

- **Emotion Detection:** The system uses a trained model to analyze facial expressions and detect emotions such as happiness, sadness, and surprise.
- **Face Recognition:** The system can recognize students' faces and match them with the stored data in the `students.json` file.
- **Student Management:** The application allows for adding new students and updating existing records, ensuring that the database is current and accurate.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.