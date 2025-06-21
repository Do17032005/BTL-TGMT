import cv2
import numpy as np
import json
import os
import logging

def load_student_data(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Student data file not found: {file_path}")
        return {}
    
    with open(file_path, 'r') as file:
        student_data = json.load(file)
    
    return student_data

def save_student_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def preprocess_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(gray_image, (200, 200))
    return resized_image

def log_message(message):
    logging.info(message)

def setup_logging(log_file='app.log'):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')