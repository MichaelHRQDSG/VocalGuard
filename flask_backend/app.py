import os
from flask import Flask, request, jsonify
import subprocess
from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import PatternFill, Font
from flask_cors import CORS
from upload import upload
import json
import uuid



app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
# 模拟的用户数据存储
users = {}
audio_data = {}  # 定义音频数据字典

# 示例威胁数据
threat_data = [
    {"description": "Threat 1: Unusual login attempts"},
    {"description": "Threat 2: Suspicious IP addresses"},
    {"description": "Threat 3: Malware detected"},
    {"description": "Threat 4: Data exfiltration detected"},
    {"description": "Threat 5: Unauthorized access to sensitive files"},
]
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API!"}), 200
# Endpoint to upload the audio file and generate a unique ID
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received request at /upload")
    print("Request files:", request.files)
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['audioFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Generate a unique ID for the audio file
    audio_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{audio_id}{file_extension}"

    # Save the audio file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    # Store audio metadata
    audio_data[audio_id] = {
        'is_synthetic': None,
        'is_specified_speaker': None,
        'speaker_id': None,
        'transcription': None,
        'task': None,
        'storage_path': file_path
    }

    # Return the audio ID and a success message
    return jsonify({
        'message': 'File uploaded successfully',
        'audio_id': audio_id,
        'path': file_path
    }), 200

# Endpoint to start detection based on the audio ID
@app.route('/start-detection', methods=['POST'])
def start_detection():
    data = request.json
    audio_id = data.get('audio_id')

    if audio_id not in audio_data:
        return jsonify({'error': 'Invalid audio ID'}), 400

    # Process the audio file (placeholder logic, replace with actual)
    file_path = audio_data[audio_id]['storage_path']
    audio_data[audio_id]['is_synthetic'] = True  # Example value
    audio_data[audio_id]['is_specified_speaker'] = False  # Example value
    audio_data[audio_id]['speaker_id'] = '12345'  # Example value
    audio_data[audio_id]['transcription'] = 'This is a transcribed text.'  # Example value
    audio_data[audio_id]['task'] = 'Audio Analysis Task'  # Example value

    # Return updated metadata
    return jsonify({'audio_id': audio_id, 'metadata': audio_data[audio_id]}), 200

# @app.route('/upload-and-detect', methods=['POST'])
# def upload_and_detect():
#     if 'audioFile' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['audioFile']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     # Generate a unique ID for the audio file
#     audio_id = str(uuid.uuid4())
#     file_extension = os.path.splitext(file.filename)[1]
#     unique_filename = f"{audio_id}{file_extension}"

#     # Save the audio file
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
#     try:
#         file.save(file_path)
#     except Exception as e:
#         return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

#     # Simulate detection logic (replace with actual detection code)
#     audio_data[audio_id] = {
#         'is_synthetic': True,  # Example value
#         'is_specified_speaker': False,  # Example value
#         'speaker_id': '12345',  # Example value
#         'transcription': 'This is a transcribed text.',  # Example value
#         'task': 'Audio Analysis Task',  # Example value
#         'storage_path': file_path
#     }

#     # Return the audio ID, path, and metadata
#     return jsonify({
#         'message': 'File uploaded and detection completed successfully',
#         'audio_id': audio_id,
#         'path': file_path,
#         'metadata': audio_data[audio_id]
#     }), 200
# 定义文件路径
USERS_FILE = 'users.json'

# 读取用户数据的函数
def load_users():
    if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:  # 检查文件是否存在且非空
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果文件内容无效，返回空字典并记录错误
            print("Error: JSON file is invalid, initializing as empty dictionary.")
            return {}
    return {}  # 如果文件为空或不存在，返回空字典

# 保存用户数据的函数
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# 登录功能
@app.route('/login', methods=['POST'])
def login():
    users = load_users()
    data = request.json
    email = data.get('email')
    password = data.get('password')
    print("Received request at /upload")

    if email not in users or users[email] != password:
        return jsonify({"message": "Invalid email or password."}), 401

    return jsonify({"message": "Login successful."}), 200

# 注册功能
@app.route('/register', methods=['POST'])
def register():
    users = load_users()
    data = request.json
    email = data.get('email')
    password = data.get('password')
    print("email:",email)

    # 检查用户是否已存在
    if email in users:
        return jsonify({"message": "User already exists."}), 400

    # 添加新用户
    users[email] = password
    save_users(users)

    return jsonify({"message": "Registration successful."}), 201

@app.route('/threat-monitoring', methods=['GET'])
def get_threat_data():
    return jsonify(threat_data)

def run_python_script(file_path):
    # 假设这是用于处理音频的Python脚本, 并生成result.txt文件
    subprocess.run(['python3', 'process_audio.py', file_path])
    return 'result.txt'

if __name__ == '__main__':
    app.run()