from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
import uuid
import cv2
import base64
import numpy as np
from collections import defaultdict

# Import emotion detection system
from emotion_detection import EmotionDetectionSystem

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Cấu hình
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'src/data/uploads'
app.config['RESULTS_FOLDER'] = 'src/data/results'

# Tạo thư mục nếu chưa tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Khởi tạo emotion detection system
emotion_system = EmotionDetectionSystem()

# Cache cho thống kê
statistics_cache = {
    'data': None,
    'last_updated': None,
    'cache_duration': 300  # 5 phút
}

# Các file được phép upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    """Kiểm tra file có được phép upload không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_cached_statistics():
    """Lấy thống kê từ cache nếu còn hợp lệ"""
    if (statistics_cache['data'] and statistics_cache['last_updated'] and 
        (datetime.now() - statistics_cache['last_updated']).seconds < statistics_cache['cache_duration']):
        return statistics_cache['data']
    return None

def update_statistics_cache(data):
    """Cập nhật cache thống kê"""
    statistics_cache['data'] = data
    statistics_cache['last_updated'] = datetime.now()

def calculate_statistics_from_files():
    """Tính toán thống kê từ các file kết quả"""
    try:
        results_files = [f for f in os.listdir(app.config['RESULTS_FOLDER']) 
                        if f.endswith('.json')]
        
        all_results = []
        successful_analyses = 0
        emotion_distribution = defaultdict(int)
        
        for filename in results_files:
            file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    
                    # Xử lý các loại kết quả khác nhau
                    if isinstance(result, dict):
                        if 'results' in result and result.get('success', False):
                            # Kết quả phân tích đơn lẻ
                            all_results.append(result)
                            successful_analyses += 1
                            
                            # Thống kê cảm xúc
                            if 'results' in result and 'dominant_emotion' in result['results']:
                                dominant_emotion = result['results']['dominant_emotion']
                                emotion_distribution[dominant_emotion] += 1
                                
                        elif 'total_files' in result and 'statistics' in result:
                            # Kết quả batch analysis
                            all_results.append(result)
                            successful_analyses += result.get('total_files', 0)
                            
                            # Thống kê cảm xúc từ batch
                            if 'statistics' in result and 'emotion_distribution' in result['statistics']:
                                for emotion, count in result['statistics']['emotion_distribution'].items():
                                    emotion_distribution[emotion] += count
                                    
                        elif 'source' in result and result.get('success', False):
                            # Kết quả camera
                            all_results.append(result)
                            successful_analyses += 1
                            
                            if 'results' in result and 'dominant_emotion' in result['results']:
                                dominant_emotion = result['results']['dominant_emotion']
                                emotion_distribution[dominant_emotion] += 1
                                
            except Exception as e:
                logger.warning(f"Không thể đọc file {filename}: {str(e)}")
                continue
        
        # Tính tỷ lệ thành công
        total_files = len(all_results)
        success_rate = successful_analyses / total_files if total_files > 0 else 0
        
        statistics = {
            'successful_analyses': successful_analyses,
            'total_files': total_files,
            'success_rate': success_rate,
            'emotion_distribution': dict(emotion_distribution)
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Lỗi khi tính toán thống kê: {str(e)}")
        return {
            'successful_analyses': 0,
            'total_files': 0,
            'success_rate': 0,
            'emotion_distribution': {}
        }

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_emotion():
    """
    API endpoint để phân tích cảm xúc từ ảnh
    """
    try:
        # Kiểm tra file trong request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy file ảnh'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Chưa chọn file'
            }), 400
        
        if file and file.filename and allowed_file(file.filename):
            # Tạo tên file an toàn
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Lưu file
            file.save(file_path)
            logger.info(f"Đã lưu file: {file_path}")
            
            # Phân tích cảm xúc
            result = emotion_system.analyze_emotion_from_image(file_path)
            
            # Lưu kết quả
            result_filename = f"result_{unique_filename}.json"
            result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
            emotion_system.save_results(result, result_path)
            
            # Thêm thông tin file
            result['uploaded_file'] = unique_filename
            result['result_file'] = result_filename
            
            # Invalidate cache
            statistics_cache['data'] = None
            
            return jsonify(result)
        
        else:
            return jsonify({
                'success': False,
                'error': 'File không được hỗ trợ. Chỉ chấp nhận: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400
    
    except Exception as e:
        logger.error(f"Lỗi khi xử lý request: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/api/camera-analyze', methods=['POST'])
def camera_analyze():
    """
    API endpoint để phân tích cảm xúc từ camera stream
    """
    try:
        # Lấy dữ liệu base64 từ request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy dữ liệu ảnh'
            }), 400
        
        # Decode base64 image
        image_data = data['image']
        if image_data.startswith('data:image'):
            # Loại bỏ header data:image/jpeg;base64,
            image_data = image_data.split(',')[1]
        
        # Decode base64 thành bytes
        image_bytes = base64.b64decode(image_data)
        
        # Chuyển thành numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({
                'success': False,
                'error': 'Không thể decode ảnh'
            }), 400
        
        # Lưu ảnh tạm thời
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_filename = f"camera_{timestamp}.jpg"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        cv2.imwrite(temp_path, image)
        
        # Phân tích cảm xúc
        result = emotion_system.analyze_emotion_from_image(temp_path)
        
        # Thêm thông tin camera
        result['source'] = 'camera'
        result['timestamp'] = timestamp
        
        # Lưu kết quả nếu thành công
        if result.get('success', False):
            result_filename = f"camera_result_{timestamp}.json"
            result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
            emotion_system.save_results(result, result_path)
            result['result_file'] = result_filename
        
        # Xóa file tạm
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Invalidate cache
        statistics_cache['data'] = None
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Lỗi khi phân tích camera: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/api/detect-faces', methods=['POST'])
def detect_faces():
    """
    API endpoint để detect khuôn mặt
    """
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy file ảnh'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Chưa chọn file'
            }), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            file.save(file_path)
            
            # Detect khuôn mặt
            result = emotion_system.detect_faces(file_path)
            
            return jsonify(result)
        
        else:
            return jsonify({
                'success': False,
                'error': 'File không được hỗ trợ'
            }), 400
    
    except Exception as e:
        logger.error(f"Lỗi khi detect khuôn mặt: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    API endpoint để phân tích nhiều ảnh cùng lúc
    """
    try:
        files = request.files.getlist('images')
        
        if not files:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy file ảnh'
            }), 400
        
        results = []
        uploaded_files = []
        successful_count = 0
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                file.save(file_path)
                uploaded_files.append(unique_filename)
                
                # Phân tích cảm xúc
                result = emotion_system.analyze_emotion_from_image(file_path)
                results.append(result)
                
                if result.get('success', False):
                    successful_count += 1
        
        # Tính thống kê
        statistics = emotion_system.get_emotion_statistics(results)
        
        # Lưu kết quả batch
        batch_result = {
            'batch_id': str(uuid.uuid4()),
            'analysis_time': datetime.now().isoformat(),
            'total_files': len(uploaded_files),
            'successful_analyses': successful_count,
            'statistics': statistics,
            'results': results
        }
        
        batch_filename = f"batch_result_{batch_result['batch_id']}.json"
        batch_path = os.path.join(app.config['RESULTS_FOLDER'], batch_filename)
        emotion_system.save_results(batch_result, batch_path)
        
        # Invalidate cache
        statistics_cache['data'] = None
        
        return jsonify(batch_result)
    
    except Exception as e:
        logger.error(f"Lỗi khi batch analyze: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    API endpoint để lấy thống kê từ các file kết quả đã lưu
    """
    try:
        # Kiểm tra cache trước
        cached_data = get_cached_statistics()
        if cached_data:
            return jsonify(cached_data)
        
        # Tính toán thống kê mới
        statistics = calculate_statistics_from_files()
        
        # Tạo response
        response_data = {
            'success': True,
            'total_files_analyzed': statistics['total_files'],
            'statistics': statistics
        }
        
        # Cập nhật cache
        update_statistics_cache(response_data)
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Lỗi server: {str(e)}'
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<filename>')
def result_file(filename):
    """Serve result files"""
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

@app.errorhandler(413)
def too_large(e):
    """Handler cho file quá lớn"""
    return jsonify({
        'success': False,
        'error': 'File quá lớn. Kích thước tối đa: 16MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handler cho 404"""
    return jsonify({
        'success': False,
        'error': 'Endpoint không tồn tại'
    }), 404

if __name__ == '__main__':
    logger.info("Khởi động Emotion Detection Web API...")
    app.run(debug=True, host='0.0.0.0', port=5000) 
    print("link: http://localhost:5000") 
