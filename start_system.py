#!/usr/bin/env python3
"""
Script khởi động hệ thống nhận diện cảm xúc
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Kiểm tra dependencies"""
    print("🔍 Kiểm tra dependencies...")
    
    required_packages = [
        'flask',
        'deepface',
        'opencv-python',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - chưa cài đặt")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Thiếu packages: {', '.join(missing_packages)}")
        print("Chạy lệnh sau để cài đặt:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_deepface_installation():
    """Kiểm tra cài đặt DeepFace"""
    print("\n🔍 Kiểm tra cài đặt DeepFace...")
    
    deepface_path = Path("model/deepface")
    if not deepface_path.exists():
        print("❌ Không tìm thấy thư mục model/deepface")
        return False
    
    setup_py = deepface_path / "setup.py"
    if not setup_py.exists():
        print("❌ Không tìm thấy setup.py trong model/deepface")
        return False
    
    print("✅ Tìm thấy DeepFace source code")
    return True

def install_deepface():
    """Cài đặt DeepFace"""
    print("\n📦 Cài đặt DeepFace...")
    
    try:
        # Chuyển đến thư mục deepface
        os.chdir("model/deepface")
        
        # Cài đặt DeepFace
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cài đặt DeepFace thành công")
            os.chdir("../..")
            return True
        else:
            print(f"❌ Lỗi cài đặt DeepFace: {result.stderr}")
            os.chdir("../..")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi cài đặt DeepFace: {e}")
        os.chdir("../..")
        return False

def create_directories():
    """Tạo các thư mục cần thiết"""
    print("\n📁 Tạo thư mục cần thiết...")
    
    directories = [
        "src/data/uploads",
        "src/data/results",
        "src/data/images"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")

def start_web_server():
    """Khởi động web server"""
    print("\n🚀 Khởi động web server...")
    
    try:
        # Chuyển đến thư mục main
        os.chdir("src/main")
        
        print("🌐 Web server đang khởi động...")
        print("📱 Truy cập: http://localhost:5000")
        print("⏹️  Nhấn Ctrl+C để dừng server")
        
        # Mở trình duyệt sau 3 giây
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open("http://localhost:5000")
            except:
                pass
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Khởi động Flask app
        subprocess.run([sys.executable, "app.py"])
        
    except KeyboardInterrupt:
        print("\n⏹️  Dừng server...")
    except Exception as e:
        print(f"❌ Lỗi khi khởi động server: {e}")
    finally:
        os.chdir("../..")

def main():
    """Hàm chính"""
    print("🎭 Hệ Thống Nhận Diện Cảm Xúc")
    print("=" * 40)
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n❌ Vui lòng cài đặt dependencies trước")
        return False
    
    # Kiểm tra DeepFace
    if not check_deepface_installation():
        print("\n❌ Vui lòng kiểm tra cài đặt DeepFace")
        return False
    
    # Cài đặt DeepFace nếu cần
    try:
        import deepface
        print("✅ DeepFace đã được cài đặt")
    except ImportError:
        print("📦 Cài đặt DeepFace...")
        if not install_deepface():
            print("❌ Không thể cài đặt DeepFace")
            return False
    
    # Tạo thư mục
    create_directories()
    
    # Khởi động server
    start_web_server()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1) 