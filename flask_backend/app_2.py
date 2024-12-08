import os
from flask import Flask, request, jsonify
import subprocess
from openpyxl import Workbook
from datetime import datetime
from openpyxl.styles import PatternFill, Font
from flask_cors import CORS
import json
import uuid
from pydub import AudioSegment
import time
import shutil
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
UPLOAD_FOLDER = 'uploads'
USER_FOLDER = 'user_folder'
COMPANY_FOLDER = 'company_info_folder'
THREAT_FOLDER = 'threat'
CUR_FILE_PATH = 'metadata.json'
AUDIO_DB_FOLDER = 'DB'
LLama_env='autoTest'
trans_env='openvoice'
bert_env='bert'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(USER_FOLDER, exist_ok=True)
os.makedirs(COMPANY_FOLDER, exist_ok=True)
os.makedirs(THREAT_FOLDER, exist_ok=True)
os.makedirs(AUDIO_DB_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['USER_FOLDER'] = USER_FOLDER
app.config['COMPANY_FOLDER'] = COMPANY_FOLDER
app.config['THREAT_FOLDER'] = THREAT_FOLDER
app.config['AUDIO_DB_FOLDER'] = AUDIO_DB_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
USERS_FILE = 'users.json'
CURRENT_FILE_JSON = '../current_processing.json'  # Path to store the current processing file information
from werkzeug.utils import secure_filename

# Simulated user data storage
users = {}
audio_data = {}  # Dictionary to store audio metadata

# Sample threat data
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

def generate_solution_with_llama3(json_file_path):
    # Load the detection results from the JSON file
    with open(json_file_path, 'r') as json_file:
        detection_results = json.load(json_file)

    # Construct a prompt for LLama3 using detection results
    prompt = f"""
    Based on the following detection results:
    {json.dumps(detection_results, indent=4)}
    
    Generate a response plan with the following structure:
    Task: 
    Responsible Departments: 
      - Legal Department Task:
      - Business Department Task:
      - Algorithm Department Task:
      - Customer Service Task:
    
    Provide specific and actionable tasks for each department to handle the situation.
    """

    # Call LLama3 model with the constructed prompt
    try:
        llama3_output = subprocess.run(
            ['python', 'llama3_generate.py', prompt],  # Assuming 'llama3_generate.py' is your script for interacting with LLama3
            capture_output=True, text=True, check=True
        )
        solution_content = llama3_output.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error generating solution with LLama3: {e.stderr or e.output}")
        solution_content = {
            "error": "Failed to generate solution using LLama3.",
            "details": e.stderr or e.output
        }

    # Save the generated solution to a new JSON file
    solution_file_path = os.path.splitext(json_file_path)[0] + '_solution.json'
    with open(solution_file_path, 'w') as solution_file:
        if isinstance(solution_content, str):
            try:
                # Convert string response to dictionary if possible
                solution_content = json.loads(solution_content)
            except json.JSONDecodeError:
                # If it fails, save as plain text
                solution_content = {"llama3_response": solution_content}
        json.dump(solution_content, solution_file, indent=4)

    print(f"Solution generated and saved to {solution_file_path}.")
    return solution_file_path

def update_current_processing_file(file_path):
    # Construct the path to the fixed JSON file named 'metadata.json'
    json_file_path = "./metadata.json"
    
    try:
        # Check if the JSON file exists
        if os.path.exists(json_file_path):
            # Clear the contents of the file
            with open(json_file_path, 'w') as json_file:
                json_file.write('{}')  # Write an empty JSON object
            print(f"Cleared existing JSON file at {json_file_path}")
        else:
            # Create the file if it doesn't exist
            with open(json_file_path, 'w') as json_file:
                json.dump({}, json_file, indent=4)  # Write an empty JSON object
            print(f"Created new JSON file at {json_file_path}")

        # Now, update the JSON file with the new content
        metadata = {
            'storage_path': file_path  # Update with the current audio file path
        }
        with open(json_file_path, 'w') as json_file:
            json.dump(metadata, json_file, indent=4)
        
        print(f"Updated JSON file at {json_file_path} with the new file path.")
    except Exception as e:
        print(f"Error updating JSON file: {e}")
# Upload audio file and generate unique ID
# ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'flac', 'txt', 'mp4'}
# ALLOWED_MIME_TYPES = {'audio/wav', 'audio/mpeg', 'audio/ogg', 'audio/flac', 'text/plain', 'video/mp4'}

# def allowed_file(filename):
#     """检查文件扩展名是否在允许的列表中。"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def allowed_mime_type(mime_type):
#     """检查文件 MIME 类型是否在允许的列表中。"""
#     return mime_type in ALLOWED_MIME_TYPES

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     print("Received request at /upload")
#     print("Received request",request.files)
#     try:
#         # 检查文件部分是否存在
#         if 'audioFile' not in request.files:
#             return jsonify({'error': 'No file part in request'}), 400

#         file = request.files['audioFile']
#         if file.filename.endswith('.wav'):
#             file_type = 'audio/wav'
#         else:
#             return jsonify({'error': 'Unsupported file type'}), 400
#         print(f"File type: {file.content_type}")  # 打印文件类型
#         print(f"File name: {file.filename}")      # 打印文件名

#         # 检查文件名是否为空
#         if file.filename == '':
#             return jsonify({'error': 'No selected file'}), 400

#         # 检查文件扩展名和 MIME 类型
#         # if not allowed_file(file.filename) or not allowed_mime_type(file.content_type):
#         #     return jsonify({'error': 'Invalid file type. Only WAV, MP3, OGG, and FLAC files are allowed.'}), 400

#         # 生成唯一 ID 并保存文件
#         audio_id = str(uuid.uuid4())
#         file_extension = os.path.splitext(file.filename)[1]
#         unique_filename = f"{audio_id}{file_extension}"
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(unique_filename))

#         # 保存文件
#         file.save(file_path)

#         # 存储音频元数据
#         audio_data[audio_id] = {
#             'is_synthetic': None,
#             'is_specified_speaker': None,
#             'speaker_id': None,
#             'transcription': None,
#             'task': None,
#             'storage_path': file_path
#         }

#         return jsonify({
#             'message': 'File uploaded successfully',
#             'audio_id': audio_id,
#             'path': file_path
#         }), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
import base64
from flask import Flask, request, jsonify

@app.route('/upload_dataform', methods=['POST'])
def upload_file_dataform():
    print("Received request at /upload_dataform")

    # Check if the request has the audio file part
    if 'audioFile' not in request.files:
        return jsonify({'error': 'No audio file received'}), 400

    # Get the audio file from the request
    audio_file = request.files['audioFile']

    # Check for empty file
    if audio_file.filename == '':
        return jsonify({'error': 'Empty audio file'}), 400

    # Get user information from the form data
    user_info = request.form.get('userInfo', '{}')
    try:
        user_info = json.loads(user_info)  # Parse the JSON string to a dictionary
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid userInfo format'}), 400

    user_name = user_info.get('name', 'Unknown User')
    user_level = user_info.get('level', 'Unknown Level')
    detection_info = user_info.get('detection_info', False)

    # Save the uploaded audio file temporarily
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    audio_id = str(uuid.uuid4())
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{audio_id}")
    print(temp_file_path)

    # Save the file with its original extension
    original_extension = os.path.splitext(audio_file.filename)[1].lower()
    if original_extension not in ['.wav', '.mp3', '.flac']:  # Example extension validation
        return jsonify({'error': 'Unsupported audio file format'}), 400

    temp_file_path += original_extension
    audio_file.save(temp_file_path)
    print(temp_file_path)

    # Check the audio format
    try:
        if original_extension != '.wav':
            # Load the audio file using pydub (ffmpeg backend)
            audio = AudioSegment.from_file(temp_file_path)
            wav_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{audio_id}.wav")
            audio.export(wav_file_path, format="wav")
            os.remove(temp_file_path)  # Remove the temporary file after conversion
        else:
            # Check if it can be processed as a .wav file directly
            wav_file_path = temp_file_path  # No conversion needed
    except Exception as e:
        print(f"Error processing or converting audio: {e}")
        os.remove(temp_file_path)  # Clean up temp file if conversion fails
        return jsonify({'error': f'Failed to process or convert audio: {str(e)}'}), 500
    
    update_current_processing_file(wav_file_path)
    # Create the corresponding JSON file
    json_file_path = os.path.splitext(wav_file_path)[0] + '.json'
    metadata = {
        'user_name': user_name,
        'user_level': user_level,
        'is_synthetic': None,
        'is_specified_speaker': None,
        'speaker_id': None,
        'transcription': None,
        'task': 'Audio Analysis Task',
        'deepfake': {
            'completed': False,
            'result': {}
        },
        'query_speakers': {
            'completed': False,
            'result': {}
        },
        'detection_context': {
            'completed': False,
            'result': {}
        }
    }
    # Assuming this function is defined elsewhere
    # update_current_processing_file(wav_file_path)

    # Save metadata to the JSON file
    with open(json_file_path, 'w',encoding='utf-8') as json_file:
        json.dump(metadata, json_file, indent=4)

    return jsonify({'message': 'File uploaded successfully', 'audio_id': audio_id}), 200

    # 定义存储路径
DATA_DIR = "./url_text_data"
URL_METADATA_FILE = os.path.join("url_metadata.json")
EMAIL_METADATA_FILE = os.path.join("email_metadata.json")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化 metadata 文件
if not os.path.exists(URL_METADATA_FILE):
    with open(URL_METADATA_FILE, "w") as f:
        json.dump({"file_path": []}, f)

if not os.path.exists(EMAIL_METADATA_FILE):
    with open(EMAIL_METADATA_FILE, "w") as f:
        json.dump({"file_path": []}, f)


def is_valid_url(text):
    """检查是否是有效的 URL"""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def save_to_json_file(data, metadata_file):
    """保存数据到 JSON 文件，并更新 metadata 文件"""
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{unique_id}.json"
    file_path = os.path.join(DATA_DIR, file_name)

    # 保存数据到文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 更新 metadata 文件
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump({"file_path": file_path}, f, ensure_ascii=False, indent=4)

    return file_path

@app.route('/upload-url', methods=['POST'])
def upload_url():
    """处理 URL 上传"""
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"message": "No text provided"}), 400

    if is_valid_url(text):
        # 如果是 URL，解析其 HTML 内容为纯文本
        try:
            response = requests.get(text)
            soup = BeautifulSoup(response.content, "html.parser")
            text_content = soup.get_text()
        except Exception as e:
            return jsonify({"message": f"Failed to fetch URL content: {str(e)}"}), 500

        # 保存解析后的文本到文件
        file_path = save_to_json_file({"url": text, "content": text_content}, URL_METADATA_FILE)
        file_path = save_to_json_file(
            {
                "url": text, 
                "text": text_content,
                "classification": "None",
                "confidence": "None",
                "threat_phrases": "None"
            },
            URL_METADATA_FILE
        )
        return jsonify({"result": f"URL processed and saved to {file_path}"})
    else:
        # 如果是普通文本，直接保存
        file_path = save_to_json_file(
            {
                "text": text,
                "classification": "None",
                "confidence": "None",
                "threat_phrases": "None"
            },
            URL_METADATA_FILE
        )
        return jsonify({"result": f"Text processed and saved to {file_path}"})

@app.route('/url-detection', methods=['POST'])
def run_subprocess():
    """
    调用子程序，读取生成的 JSON 文件内容并返回。
    """
    try:
        # 调用外部 .py 文件
        # 假设外部程序是 "generate_json.py"，它会生成 `OUTPUT_JSON_FILE`
        subprocess.run([f"conda run -n {bert_env} python ./toxic_bert.py"], check=True)

        # 检查 JSON 文件是否存在
        if not os.path.exists(OUTPUT_JSON_FILE):
            return jsonify({"error": "JSON file not found"}), 404

        # 读取 JSON 文件内容
        with open(OUTPUT_JSON_FILE, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # 返回 JSON 数据
        return jsonify({"message": "Subprocess executed successfully", "data": json_data})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Subprocess failed: {e}"}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to decode JSON: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/upload-email', methods=['POST'])
def upload_email():
    """处理邮件上传"""
    data = request.json
    email_text = data.get("emailText", "")

    if not email_text:
        return jsonify({"message": "No email text provided"}), 400

    # 保存邮件文本到文件
    file_path = save_to_json_file({"email": email_text}, EMAIL_METADATA_FILE)
    return jsonify({"result": f"Email processed and saved to {file_path}"})

# @app.route('/upload-personal-info', methods=['POST'])
# def upload_personal_info():
#     try:
#         # Ensure the request is JSON
#         if not request.is_json:
#             print("Request content type is not JSON.")
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         data = request.json
#         print("Received data:", data)  # Debug: Print received data

#         user_info = data.get('userInfo', {})
#         profile_photo = data.get('profilePhoto', None)  # Expecting a base64 string for the profile photo
#         audio_info = data.get('audioInfo', None)  # Expecting a base64 string for the audio file
#         personal_intro = data.get('personalIntro', '')

#         # Check for required fields
#         if not profile_photo or not audio_info or not personal_intro:
#             print("Missing fields in the request.")
#             return jsonify({'error': 'All fields (profile photo, audio info, personal introduction) are required.'}), 400

#         # Process the profile photo
#         if profile_photo.startswith('data:'):
#             header, base64_data = profile_photo.split(',', 1)
#             profile_photo_data = base64.b64decode(base64_data)
#             profile_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.jpg")

#             with open(profile_photo_path, 'wb') as photo_file:
#                 photo_file.write(profile_photo_data)
#             print(f"Profile photo saved at: {profile_photo_path}")  # Debug: Confirm file save
#         else:
#             print("Invalid profile photo format.")
#             return jsonify({'error': 'Invalid profile photo format'}), 400

#         # Process the audio information
#         if audio_info.startswith('data:'):
#             header, base64_data = audio_info.split(',', 1)
#             audio_info_data = base64.b64decode(base64_data)
#             audio_info_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.mp3")

#             with open(audio_info_path, 'wb') as audio_file:
#                 audio_file.write(audio_info_data)
#             print(f"Audio info saved at: {audio_info_path}")  # Debug: Confirm file save
#         else:
#             print("Invalid audio info format.")
#             return jsonify({'error': 'Invalid audio info format'}), 400

#         # Save the personal introduction and paths to a JSON file or database
#         personal_info_metadata = {
#             'user_name': user_info.get('name', 'Unknown User'),
#             'user_level': user_info.get('level', 'Unknown Level'),
#             'profile_photo_path': profile_photo_path,
#             'audio_info_path': audio_info_path,
#             'personal_intro': personal_intro,
#             'timestamp': datetime.now().isoformat()
#         }

#         personal_info_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}.json")
#         with open(personal_info_file_path, 'w') as json_file:
#             json.dump(personal_info_metadata, json_file, indent=4)

#         return jsonify({'message': 'Personal information uploaded successfully', 'metadata': personal_info_metadata}), 200

#     except Exception as e:
#         print("Error occurred:", str(e))  # Debug: Print error message
#         return jsonify({'error': str(e)}), 500


TEMP_IMG_FOLDER = 'temp_img'
if not os.path.exists(TEMP_IMG_FOLDER):
    os.makedirs(TEMP_IMG_FOLDER)

# Define user file structure
USERFILE_FOLDER = 'userfile'
if not os.path.exists(USERFILE_FOLDER):
    os.makedirs(USERFILE_FOLDER)

# JSON file to store verification data
REVERIFY_JSON_PATH = 're_verify.json'

# Function to read and write to the JSON file
def read_reverify_json():
    if os.path.exists(REVERIFY_JSON_PATH):
        with open(REVERIFY_JSON_PATH, 'r') as f:
            return json.load(f)
    return {}

# def write_reverify_json(data):
#     with open(REVERIFY_JSON_PATH, 'w') as f:
#         json.dump(data, f, indent=4)
def write_reverify_json(data):
    with open(REVERIFY_JSON_PATH, 'w') as f:
        f.truncate(0)  # 清空文件内容
        json.dump(data, f, indent=4)  # 写入新数据


def clear_temp_folder():
    """Function to clear the contents of the TEMP_IMG_FOLDER."""
    if os.path.exists(TEMP_IMG_FOLDER):
        shutil.rmtree(TEMP_IMG_FOLDER)  # Remove the directory and all its contents
    os.makedirs(TEMP_IMG_FOLDER, exist_ok=True)  # Recreate the directory

@app.route('/upload-images', methods=['POST'])
def upload_images():
    username = request.form.get('username')
    audio_url = request.form.get('audio_url')
    json_url= os.path.splitext(audio_url)[0] + '.json'
    print(json_url)
    files = request.files.getlist('image1') + request.files.getlist('image2') + request.files.getlist('image3')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    if not files:
        return jsonify({'error': 'No images uploaded'}), 400

    clear_temp_folder()
    saved_files = []
    user_folder_path = os.path.join(USERFILE_FOLDER, username, 'img')
    os.makedirs(user_folder_path, exist_ok=True)
    os.makedirs(TEMP_IMG_FOLDER, exist_ok=True)

    for idx, file in enumerate(files):
        if file:
            # Save image to temp folder
            temp_filename = secure_filename(f"{username}_temp_image{idx + 1}.png")
            temp_filepath = os.path.join(TEMP_IMG_FOLDER, temp_filename)
            file.save(temp_filepath)

            # Save image to user-specific folder
            user_filename = secure_filename(f"{username}_image{idx + 1}.png")
            user_filepath = os.path.join(user_folder_path, user_filename)
            os.makedirs(os.path.dirname(user_filepath), exist_ok=True)
            with open(temp_filepath, 'rb') as src, open(user_filepath, 'wb') as dst:
                dst.write(src.read())

            saved_files.append({
                'temp_path': temp_filepath,
                'user_path': user_filepath
            })
        else:
            print("No valid image found")

    # Read existing data and update JSON file
    reverify_data = read_reverify_json()
    reverify_data[username] = {
        'images': saved_files
    }
    write_reverify_json(reverify_data)

    try:
        # Run FR.py and capture the output
        subprocess.run(
            f'conda run -n paddlepaddle python ./FR.py',
            shell=True, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running FR.py: {e.stderr or e.output}")
        return jsonify({'error': 'Error during face recognition process'}), 500

    # Read the updated JSON file
    updated_data = read_reverify_json()

    
    if username in updated_data:
        verification_result = updated_data[username].get('verification_result', False)
        print(verification_result)
        reason = updated_data[username].get('reason', 'No reason provided')
        if verification_result:
            try:
                if os.path.exists(json_url):
                    with open(json_url, 'r') as file:
                        json_data = json.load(file)
                    print(json_data)
                    # Update the threat_score if it exists
                    if "threat_score" in json_data :
                        json_data['threat_score'] = 0
                        with open(json_url, 'w') as file:
                            json.dump(json_data, file, indent=4)
                else:
                    print(f"JSON file not found: {json_url}")
            except Exception as e:
                print(f"Error updating JSON file: {e}")
                return jsonify({'error': 'Error updating threat score in JSON file'}), 500
            mapping_file_path = 'threat/speaker_audio_mapping.json'  # Replace with your actual path
            if os.path.exists(mapping_file_path):
                with open(mapping_file_path, 'r') as file:
                    mapping_data = json.load(file)

                if username in mapping_data and mapping_data[username]:
                    # Remove the first audio entry for the user
                    removed_audio = mapping_data[username].pop(0)
                    print(f"Removed audio: {removed_audio}")

                    # If no other audio paths remain for the user, remove the user entry
                    if not mapping_data[username]:
                        del mapping_data[username]
                        print(f"User {username} removed from speaker_audio_mapping.json")

                    # Save the updated mapping data
                    with open(mapping_file_path, 'w') as file:
                        json.dump(mapping_data, file, indent=4)
                else:
                    print(f"No audio paths found for user {username} in speaker_audio_mapping.json")

        return jsonify({
            'message': 'Images uploaded and processed successfully',
            'verification_result': verification_result,
            'reason': reason,
            'threat': 0
        })

    return jsonify({'error': 'User data not found after processing'}), 404

MAPPING_FILE = os.path.join(THREAT_FOLDER, 'speaker_audio_mapping.json')

@app.route('/fetch-verification', methods=['POST'])
def fetch_verification():

    # Get the username from the incoming request
    data = request.get_json()
    username = data.get('username')
    print(username)

    if not username:
        return jsonify({"message": "Username is required."}), 400

    # Check if the mapping file exists
    if not os.path.exists(MAPPING_FILE):
        return jsonify({"message": "Mapping file not found."}), 404

    # Load mapping data
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)

    # Check if the user exists in the mapping data
    if username not in mapping_data:
        return jsonify({"message": "No pending verification files found for this user."}), 404
    
    # Iterate over the user's pending audio files
    audio_files = mapping_data.get(username, [])
    print(audio_files)
    if audio_files:
        audio_file_path = audio_files[0]
        print(audio_file_path)

        # Check for the corresponding transcription JSON file
        transcription_file_path = audio_file_path.replace('.wav', '.json')
        print(transcription_file_path)

        # Load transcription data
        with open(transcription_file_path, 'r', encoding='utf-8') as tf:
            transcription_data = json.load(tf)
            transcription = transcription_data.get('transcription', '')

        # Return the audio file URL and transcription in a JSON response
        return jsonify({
            "audio_url": audio_file_path,
            "transcription": transcription
        }), 200

    # If no files are found
    return jsonify({"message": "No pending verification files found."}), 404

@app.route('/confirm-verification', methods=['POST'])
def confirm_verification():
    data = request.get_json()

    is_user_voice = data.get('isUserVoice')
    username = data.get('username')
    print("is_user_voice:", is_user_voice)
    print("username:", username)

    if is_user_voice is None or not username:
        return jsonify({"message": "Invalid input"}), 400

    if not is_user_voice:
        # Handle the case where the user denies the request
        with open(MAPPING_FILE, 'r+') as f:
            mapping_data = json.load(f)
            # Find and remove the first entry for the specified username
            if username in mapping_data and mapping_data[username]:
                # Remove the first item in the list for this username
                removed_audio = mapping_data[username].pop(0)
                print(f"Removed audio file: {removed_audio}")
                
                # Save the updated mapping data
                f.seek(0)
                json.dump(mapping_data, f)
                f.truncate()

        return jsonify({"message": "Request denied and first data entry removed"}), 200

    # If `isUserVoice` is `true`, proceed with further steps
    return jsonify({"message": "Request confirmed. Please proceed with face verification."}), 200


@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory(filename)


@app.route('/upload-document', methods=['POST'])
def upload_document():
    try:
        # Check if a file is present in the request
        if 'documentFile' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['documentFile']
        document_type = request.form.get('documentType', 'General')  # Default to 'General' if not provided

        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected for upload'}), 400

        # Ensure the file is a PDF
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Create a directory for the document type if it doesn't exist
        document_dir = os.path.join(app.config['COMPANY_FOLDER'], document_type)

        os.makedirs(document_dir, exist_ok=True)

        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(document_dir, unique_filename)

        # Save the file
        file.save(file_path)

        # Generate a document ID (in a real application, you might use a database ID)
        document_id = str(uuid.uuid4())

        # Return a success response with the document ID
        return jsonify({
            'message': 'File uploaded successfully',
            'document_id': document_id,
            'file_path': file_path
        }), 200

    except Exception as e:
        print(f"Error occurred during document upload: {e}")
        return jsonify({'error': str(e)}), 500

# @app.route('/upload-personal-info', methods=['POST'])
# def upload_personal_info():
#     try:
#         # Ensure the request is JSON
#         if not request.is_json:
#             print("Request content type is not JSON.")
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         data = request.json
#         print("Received data:", data)  # Debug: Print received data

#         user_info = data.get('userInfo', {})
#         print(user_info)
#         email = user_info.get('name', 'unknown_user')  # Assume email is provided for creating the folder structure
#         profile_photo = data.get('profilePhoto', None)  # Expecting a base64 string for the profile photo
#         audio_info = data.get('audioInfo', None)  # Expecting a base64 string for the audio file
#         personal_intro = data.get('personalIntro', '')

#         # Check for required fields
#         if not email or not profile_photo or not audio_info or not personal_intro:
#             print("Missing fields in the request.")
#             return jsonify({'error': 'All fields (email, profile photo, audio info, personal introduction) are required.'}), 400

#         # Define user directory and subdirectories
#         base_dir = app.config['USER_FOLDER']
#         user_dir = os.path.join(base_dir, email)
#         photo_dir = os.path.join(user_dir, 'imgs')
#         audio_dir = os.path.join(user_dir, 'audio')
#         info_dir = os.path.join(user_dir, 'info')
#         db_dir = os.path.join(app.config['AUDIO_DB_FOLDER'], email)

#         # Create directories if they do not exist
#         os.makedirs(photo_dir, exist_ok=True)
#         os.makedirs(audio_dir, exist_ok=True)
#         os.makedirs(info_dir, exist_ok=True)
#         os.makedirs(db_dir, exist_ok=True)

#         # Process and save the profile photo
#         if profile_photo.startswith('data:'):
#             header, base64_data = profile_photo.split(',', 1)
#             profile_photo_data = base64.b64decode(base64_data)
#             profile_photo_path = os.path.join(photo_dir, f"{uuid.uuid4()}.jpg")
#             with open(profile_photo_path, 'wb') as photo_file:
#                 photo_file.write(profile_photo_data)
#             print(f"Profile photo saved at: {profile_photo_path}")  # Debug: Confirm file save
#         else:
#             print("Invalid profile photo format.")
#             return jsonify({'error': 'Invalid profile photo format'}), 400

#         # Process and save the audio information
#         if audio_info.startswith('data:'):
#             header, base64_data = audio_info.split(',', 1)
#             audio_info_data = base64.b64decode(base64_data)
#             audio_info_path = os.path.join(audio_dir, f"{uuid.uuid4()}.mp3")
#             with open(audio_info_path, 'wb') as audio_file:
#                 audio_file.write(audio_info_data)
#             print(f"Audio info saved at: {audio_info_path}")  # Debug: Confirm file save

#             # Convert the audio to .wav format and save to both audio_dir and db_dir
#             try:
#                 # Load the audio file using pydub
#                 audio = AudioSegment.from_file(audio_info_path)

#                 # Save the converted .wav file in audio_dir
#                 wav_file_path = os.path.splitext(audio_info_path)[0] + '.wav'
#                 audio.export(wav_file_path, format='wav')
#                 print(f"Audio converted and saved as .wav in audio_dir: {wav_file_path}")

#                 # Save another copy in db_dir with a duration limit of 10 seconds
#                 db_wav_file_path = os.path.join(db_dir, f"{uuid.uuid4()}.wav")
#                 limited_audio = audio[:12 * 1000]  # Limit to first 10 seconds (10,000 ms)
#                 limited_audio.export(db_wav_file_path, format='wav')
#                 print(f"Audio converted and saved as .wav (10s) in db_dir: {db_wav_file_path}")

#             except Exception as e:
#                 print(f"Error converting audio to .wav format: {e}")
#                 return jsonify({'error': 'Failed to convert audio to .wav format'}), 500

#         else:
#             print("Invalid audio info format.")
#             return jsonify({'error': 'Invalid audio info format'}), 400

#         # Save the personal introduction as a text file
#         personal_intro_path = os.path.join(info_dir, 'personal_intro.txt')
#         with open(personal_intro_path, 'w') as intro_file:
#             intro_file.write(personal_intro)

#         # Save metadata as a JSON file
#         personal_info_metadata = {
#             'user_name': user_info.get('name', 'Unknown User'),
#             'user_level': user_info.get('level', 'Unknown Level'),
#             'profile_photo_path': profile_photo_path,
#             'audio_info_path': audio_info_path,
#             'wav_file_path': wav_file_path,
#             'db_wav_file_path': db_wav_file_path,
#             'personal_intro_path': personal_intro_path,
#             'timestamp': datetime.now().isoformat()
#         }

#         metadata_file_path = os.path.join(info_dir, 'metadata.json')
#         with open(metadata_file_path, 'w') as json_file:
#             json.dump(personal_info_metadata, json_file, indent=4)

#         return jsonify({'message': 'Personal information uploaded successfully', 'metadata': personal_info_metadata}), 200

#     except Exception as e:
#         print("Error occurred:", str(e))  # Debug: Print error message
#         return jsonify({'error': str(e)}), 500
# import json
# import os
# import re
# import uuid
# import base64
# from datetime import datetime
# from flask import Flask, jsonify, request
# from pydub import AudioSegment

# app = Flask(__name__)

# @app.route('/upload-personal-info', methods=['POST'])
# def upload_personal_info():
#     try:
#         # Ensure the request is JSON
#         if not request.is_json:
#             print("Request content type is not JSON.")
#             return jsonify({'error': 'Request must be JSON'}), 400
        
#         data = request.json
#         print("Received data:", data)  # Debug: Print received data

#         user_info = data.get('userInfo', {})
#         print(user_info)
#         email = user_info.get('name', 'unknown_user')  # Assume email is provided for creating the folder structure
#         profile_photo = data.get('profilePhoto', None)  # Expecting a base64 string for the profile photo
#         audio_info = data.get('audioInfo', None)  # Expecting a base64 string for the audio file
#         personal_intro = data.get('personalIntro', '')

#         # Check for required fields
#         if not email or not profile_photo or not audio_info or not personal_intro:
#             print("Missing fields in the request.")
#             return jsonify({'error': 'All fields (email, profile photo, audio info, personal introduction) are required.'}), 400

#         # Define user directory and subdirectories
#         base_dir = app.config['USER_FOLDER']
#         user_dir = os.path.join(base_dir, email)
#         photo_dir = os.path.join(user_dir, 'imgs')
#         audio_dir = os.path.join(user_dir, 'audio')
#         info_dir = os.path.join(user_dir, 'info')
#         db_dir = os.path.join(app.config['AUDIO_DB_FOLDER'], email)

#         # Create directories if they do not exist
#         os.makedirs(photo_dir, exist_ok=True)
#         os.makedirs(audio_dir, exist_ok=True)
#         os.makedirs(info_dir, exist_ok=True)
#         os.makedirs(db_dir, exist_ok=True)

#         # Process and save the profile photo
#         if profile_photo.startswith('data:'):
#             header, base64_data = profile_photo.split(',', 1)
#             profile_photo_data = base64.b64decode(base64_data)
#             profile_photo_path = os.path.join(photo_dir, f"{uuid.uuid4()}.jpg")
#             with open(profile_photo_path, 'wb') as photo_file:
#                 photo_file.write(profile_photo_data)
#             print(f"Profile photo saved at: {profile_photo_path}")  # Debug: Confirm file save
#         else:
#             print("Invalid profile photo format.")
#             return jsonify({'error': 'Invalid profile photo format'}), 400

#         # Process and save the audio information
#         if audio_info.startswith('data:'):
#             header, base64_data = audio_info.split(',', 1)
#             audio_info_data = base64.b64decode(base64_data)
            
#             # Determine file format from header
#             file_extension = 'mp3'  # Default extension
#             if 'audio/wav' in header:
#                 file_extension = 'wav'
#                 print("wav")
#             elif 'audio/mpeg' in header:
#                 file_extension = 'mp3'
#                 print("mp3")
#             elif 'audio/mp4' in header or 'audio/m4a' in header:
#                 file_extension = 'm4a'
#                 print("m4a")
            
#             audio_info_path = os.path.join(audio_dir, f"{uuid.uuid4()}.{file_extension}")
#             with open(audio_info_path, 'wb') as audio_file:
#                 audio_file.write(audio_info_data)
#             print(f"Audio info saved at: {audio_info_path}")  # Debug: Confirm file save

#             # Convert the audio to .wav format and save to both audio_dir and db_dir
#             try:
#                 # Load the audio file using pydub (supports multiple formats)
#                 audio = AudioSegment.from_file(audio_info_path)

#                 # Save the converted .wav file in audio_dir
#                 wav_file_path = os.path.splitext(audio_info_path)[0] + '.wav'
#                 audio.export(wav_file_path, format='wav')
#                 print(f"Audio converted and saved as .wav in audio_dir: {wav_file_path}")

#                 # Save another copy in db_dir with a duration limit of 10 seconds
#                 db_wav_file_path = os.path.join(db_dir, f"{uuid.uuid4()}.wav")
#                 limited_audio = audio[:10 * 1000]  # Limit to first 10 seconds (10,000 ms)
#                 limited_audio.export(db_wav_file_path, format='wav')
#                 print(f"Audio converted and saved as .wav (10s) in db_dir: {db_wav_file_path}")

#             except Exception as e:
#                 print(f"Error converting audio to .wav format: {e}")
#                 return jsonify({'error': 'Failed to convert audio to .wav format'}), 500

#         else:
#             print("Invalid audio info format.")
#             return jsonify({'error': 'Invalid audio info format'}), 400

#         # Save the personal introduction as a text file
#         personal_intro_path = os.path.join(info_dir, 'personal_intro.txt')
#         with open(personal_intro_path, 'w') as intro_file:
#             intro_file.write(personal_intro)

#         # Save metadata as a JSON file
#         personal_info_metadata = {
#             'user_name': user_info.get('name', 'Unknown User'),
#             'user_level': user_info.get('level', 'Unknown Level'),
#             'profile_photo_path': profile_photo_path,
#             'audio_info_path': audio_info_path,
#             'wav_file_path': wav_file_path,
#             'db_wav_file_path': db_wav_file_path,
#             'personal_intro_path': personal_intro_path,
#             'timestamp': datetime.now().isoformat()
#         }

#         metadata_file_path = os.path.join(info_dir, 'metadata.json')
#         with open(metadata_file_path, 'w') as json_file:
#             json.dump(personal_info_metadata, json_file, indent=4)

#         return jsonify({'message': 'Personal information uploaded successfully', 'metadata': personal_info_metadata}), 200

#     except Exception as e:
#         print("Error occurred:", str(e))  # Debug: Print error message
#         return jsonify({'error': str(e)}), 500

@app.route('/upload-personal-info', methods=['POST'])
def upload_personal_info():
    try:
        # Ensure form data contains necessary parts
        user_info_json = request.form.get('userInfo')
        profile_photo = request.files.get('profilePhoto')
        audio_info = request.files.get('audioInfo')
        personal_intro = request.form.get('personalIntro')

        if not user_info_json or not profile_photo or not audio_info or not personal_intro:
            print("Missing fields in the request.")
            return jsonify({'error': 'All fields (userInfo, profile photo, audio info, personal introduction) are required.'}), 400

        user_info = json.loads(user_info_json)
        email = user_info.get('name', 'unknown_user')  # Assume email is provided for creating the folder structure

        # Define user directory and subdirectories
        base_dir = app.config['USER_FOLDER']
        user_dir = os.path.join(base_dir, email)
        photo_dir = os.path.join(user_dir, 'imgs')
        audio_dir = os.path.join(user_dir, 'audio')
        info_dir = os.path.join(user_dir, 'info')
        db_dir = os.path.join(app.config['AUDIO_DB_FOLDER'], email)

        # Create directories if they do not exist
        os.makedirs(photo_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(info_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)

        # Save the profile photo
        profile_photo_path = os.path.join(photo_dir, f"{uuid.uuid4()}.jpg")
        profile_photo.save(profile_photo_path)
        print(f"Profile photo saved at: {profile_photo_path}")

        # Save the audio information
        audio_extension = os.path.splitext(audio_info.filename)[1].lower()
        if audio_extension not in ['.mp3', '.wav', '.m4a']:
            return jsonify({'error': 'Unsupported audio format'}), 400

        audio_info_path = os.path.join(audio_dir, f"{uuid.uuid4()}{audio_extension}")
        audio_info.save(audio_info_path)
        print(f"Audio info saved at: {audio_info_path}")

        # Convert the audio to .wav format and save to both audio_dir and db_dir
        try:
            audio = AudioSegment.from_file(audio_info_path)
            wav_file_path = os.path.splitext(audio_info_path)[0] + '.wav'
            audio.export(wav_file_path, format='wav')
            print(f"Audio converted and saved as .wav in audio_dir: {wav_file_path}")

            # Save another copy in db_dir with a duration limit of 10 seconds
            db_wav_file_path = os.path.join(db_dir, f"{uuid.uuid4()}.wav")
            limited_audio = audio[:10 * 1000]  # Limit to first 10 seconds (10,000 ms)
            limited_audio.export(db_wav_file_path, format='wav')
            print(f"Audio converted and saved as .wav (10s) in db_dir: {db_wav_file_path}")

        except Exception as e:
            print(f"Error converting audio to .wav format: {e}")
            return jsonify({'error': 'Failed to convert audio to .wav format'}), 500

        # Save the personal introduction as a text file
        personal_intro_path = os.path.join(info_dir, 'personal_intro.txt')
        with open(personal_intro_path, 'w') as intro_file:
            intro_file.write(personal_intro)

        # Save metadata as a JSON file
        personal_info_metadata = {
            'user_name': user_info.get('name', 'Unknown User'),
            'user_level': user_info.get('level', 'Unknown Level'),
            'profile_photo_path': profile_photo_path,
            'audio_info_path': audio_info_path,
            'wav_file_path': wav_file_path,
            'db_wav_file_path': db_wav_file_path,
            'personal_intro_path': personal_intro_path,
            'timestamp': datetime.now().isoformat()
        }

        metadata_file_path = os.path.join(info_dir, 'metadata.json')
        with open(metadata_file_path, 'w') as json_file:
            json.dump(personal_info_metadata, json_file, indent=4)

        return jsonify({'message': 'Personal information uploaded successfully', 'metadata': personal_info_metadata}), 200

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500

def wait_for_completion(json_file_path, field='deepfake', timeout=300, interval=5):
    """Wait until the specified field in the JSON file is marked as completed."""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            print("Timeout reached while waiting for completion.")
            return False

        try:
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)
                if data.get(field, {}).get('completed') == True:
                    print(f"{field} analysis completed.")
                    return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading {json_file_path}: {e}")

        time.sleep(interval)

@app.route('/get_solution/<filename>', methods=['GET'])
def get_solution(filename):
    solution_path = os.path.join(app.config['THREAT_FOLDER'], filename)
    print(solution_path)
    if os.path.exists(solution_path):
        with open(solution_path, 'r') as solution_file:
            content = json.load(solution_file)
        return jsonify(content)
    else:
        return jsonify({'error': 'Solution file not found'}), 404
# Start detection based on audio ID
@app.route('/start-detection', methods=['POST'])
def start_detection():

    with open(CUR_FILE_PATH, 'r') as f:
            metadata = json.load(f)
    print(metadata)
    audio_id = metadata.get('storage_path')
    print(audio_id)

    # Determine the JSON file path
    json_file_path = os.path.splitext(audio_id)[0] + '.json'

    # Load existing metadata from the JSON file
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            audio_metadata = json.load(json_file)
    else:
        audio_metadata = {}

    deepfake_result = "No result"  # Default value if subprocess fails
    query_speakers_result = "No result"  # Default value for other subprocess
    detection_context_result = "No result"  # Another example if needed

    # Run deepfake.py and capture the output
    try:
        subprocess.run(
            f'python ./deepfake.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except Exception as e:
        print(f"Error starting deepfake.py: {e}")

    try:
        # Run query_speakers.py and capture the output
        subprocess.run(
            f'conda run -n {trans_env} python ./query_x_vec.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running query_speakers.py: {e.stderr or e.output}")

    print(trans_env)
    print(LLama_env)
    # Run detection_context.py and capture the output
    try:
        # Run query_speakers.py and capture the output
        subprocess.run(
            f'conda run -n {trans_env} python ./trans.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running trans.py: {e.stderr or e.output}")

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            audio_metadata = json.load(json_file)
    else:
        audio_metadata = {}
    language = audio_metadata.get('detected_language', 'en') 
    print(language)
    if language=="en":
        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {bert_env} python ./en_bert.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running en_bert.py: {e.stderr or e.output}")

        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {LLama_env} python ./LLama3_en.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running LLama3_en.py: {e.stderr or e.output}")
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)
    elif language=="zh":
        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {bert_env} python ./cn_bert.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running en_bert.py: {e.stderr or e.output}")

        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {LLama_env} python ./LLama3_en.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running LLama3_en.py: {e.stderr or e.output}")
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)
    # Calculate threat score
    threat_score = 0
    if updated_metadata.get('is_synthetic'):
        threat_score += 30
    if updated_metadata.get('is_specified_speaker'):
        threat_score += 20
    classification_result = updated_metadata.get('detection_context', {}).get('result', {}).get('classification_result', '')
    if classification_result != "Non-fraud Content"and classification_result!="非欺诈内容":
        threat_score += 20
    money_amount = updated_metadata.get('detection_context', {}).get('result', {}).get('money_amount', "None")
    if money_amount != "None":
        threat_score += 15
    time = updated_metadata.get('detection_context', {}).get('result', {}).get('time', "None")
    if time != "None":
        threat_score += 15

    # Add the threat score to the metadata
    updated_metadata['threat_score'] = threat_score
    with open(json_file_path, 'w') as json_file:
        json.dump(updated_metadata, json_file, indent=4)
    

    if updated_metadata.get('is_synthetic') or threat_score > 50:
        if not os.path.exists(THREAT_FOLDER):
            os.makedirs(THREAT_FOLDER)

        # Copy JSON file
        shutil.copy(json_file_path, os.path.join(THREAT_FOLDER, os.path.basename(json_file_path)))

        if language=="en":
            try:
            # Run query_speakers.py and capture the output
                subprocess.run(
                    f'conda run -n {LLama_env} python ./solution.py {audio_id}',
                    shell=True, capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running solution.py: {e.stderr or e.output}")
        elif language=='zh':
            try:
            # Run query_speakers.py and capture the output
                subprocess.run(
                    f'conda run -n {LLama_env} python ./cn_solution.py {audio_id}',
                    shell=True, capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running cn_solution.py: {e.stderr or e.output}")

        # Copy corresponding WAV file
        if os.path.exists(audio_id):
            shutil.copy(audio_id, os.path.join(THREAT_FOLDER, os.path.basename(audio_id)))

    if threat_score > 50:
        speaker_id = updated_metadata.get('speaker_id', 'Unknown Speaker')
        print(speaker_id)
        
        # Initialize the speaker_audio_dict if not already defined
        if 'speaker_audio_dict' not in locals():
            speaker_audio_dict = {}
        
        if speaker_id not in speaker_audio_dict:
            speaker_audio_dict[speaker_id] = []
        speaker_audio_dict[speaker_id].append(os.path.join(THREAT_FOLDER, os.path.basename(audio_id)))
        # Correcting variable name and saving the speaker-audio dictionary to a file (optional)
        speaker_dict_path = os.path.join(THREAT_FOLDER, 'speaker_audio_mapping.json')
        if os.path.exists(speaker_dict_path):
            with open(speaker_dict_path, 'r') as dict_file:
                speaker_audio_dict_old = json.load(dict_file)
        else:
            # Create an empty dictionary if the file does not exist
            speaker_audio_dict_old = {}

        # Save updated dictionary
        with open(speaker_dict_path, 'w') as dict_file:
            json.dump(speaker_audio_dict, dict_file, indent=4)
        # Save the updated metadata back to the JSON file
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)

        return jsonify(updated_metadata), 200

    return jsonify(updated_metadata), 200

@app.route('/start-smalldetection', methods=['POST'])
def start_small_detection():

    with open(CUR_FILE_PATH, 'r') as f:
            metadata = json.load(f)
    print(metadata)
    audio_id = metadata.get('storage_path')

    # Determine the JSON file path
    json_file_path = os.path.splitext(audio_id)[0] + '.json'

    # Load existing metadata from the JSON file
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            audio_metadata = json.load(json_file)
    else:
        audio_metadata = {}

    deepfake_result = "No result"  # Default value if subprocess fails
    query_speakers_result = "No result"  # Default value for other subprocess
    detection_context_result = "No result"  # Another example if needed

    # Run deepfake.py and capture the output
    try:
        subprocess.run(
            f'python ./deepfake.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except Exception as e:
        print(f"Error starting deepfake.py: {e}")
    print("deepfake detection complete!")

    try:
        # Run query_speakers.py and capture the output
        subprocess.run(
            f'conda run -n {trans_env} python ./query_x_vec.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running query_speakers.py: {e.stderr or e.output}")
    print("speaker verification complete!")
    # Run detection_context.py and capture the output
    try:
        # Run query_speakers.py and capture the output
        subprocess.run(
            f'conda run -n {trans_env} python ./trans.py {audio_id}',
            shell=True, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running trans.py: {e.stderr or e.output}")
    print("transcripstion complete!")

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            audio_metadata = json.load(json_file)
    else:
        audio_metadata = {}
    language = audio_metadata.get('detected_language', 'en') 
    if language=="en":
        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {bert_env} python ./en_bert.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running en_bert.py: {e.stderr or e.output}")
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)

    elif language=="zh":
        try:
            # Run query_speakers.py and capture the output
            subprocess.run(
                f'conda run -n {bert_env} python ./cn_bert.py {audio_id}',
                shell=True, capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running en_bert.py: {e.stderr or e.output}")
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)

    # Calculate threat score
    threat_score = 0
    if updated_metadata.get('is_synthetic'):
        threat_score += 30
    if updated_metadata.get('is_specified_speaker'):
        threat_score += 20
    classification_result = updated_metadata.get('detection_context', {}).get('result', {}).get('classification_result', '')
    if classification_result != "Non-fraud Content"and classification_result!="非欺诈内容":
        threat_score += 20
    money_amount = updated_metadata.get('detection_context', {}).get('result', {}).get('money_amount', "None")
    if money_amount != "None":
        threat_score += 15
    time = updated_metadata.get('detection_context', {}).get('result', {}).get('time', "None")
    if time != "None":
        threat_score += 15

    # Add the threat score to the metadata
    updated_metadata['threat_score'] = threat_score
    with open(json_file_path, 'w') as json_file:
        json.dump(updated_metadata, json_file, indent=4)
    

    if updated_metadata.get('is_synthetic') or threat_score > 50:
        if not os.path.exists(THREAT_FOLDER):
            os.makedirs(THREAT_FOLDER)

        # Copy JSON file
        shutil.copy(json_file_path, os.path.join(THREAT_FOLDER, os.path.basename(json_file_path)))
        # Copy corresponding WAV file
        if os.path.exists(audio_id):
            shutil.copy(audio_id, os.path.join(THREAT_FOLDER, os.path.basename(audio_id)))

    if updated_metadata.get('is_synthetic'):
        speaker_id = updated_metadata.get('speaker_id', 'Unknown Speaker')
        print(speaker_id)
        
        # Initialize the speaker_audio_dict if not already defined
        if 'speaker_audio_dict' not in locals():
            speaker_audio_dict = {}
        
        if speaker_id not in speaker_audio_dict:
            speaker_audio_dict[speaker_id] = []
        speaker_audio_dict[speaker_id].append(os.path.join(THREAT_FOLDER, os.path.basename(audio_id)))
        # Correcting variable name and saving the speaker-audio dictionary to a file (optional)
        speaker_dict_path = os.path.join(THREAT_FOLDER, 'speaker_audio_mapping.json')
        if os.path.exists(speaker_dict_path):
            with open(speaker_dict_path, 'r') as dict_file:
                speaker_audio_dict_old = json.load(dict_file)
        else:
            # Create an empty dictionary if the file does not exist
            speaker_audio_dict_old = {}

        # Save updated dictionary
        with open(speaker_dict_path, 'w') as dict_file:
            json.dump(speaker_audio_dict, dict_file, indent=4)
        # Save the updated metadata back to the JSON file
        with open(json_file_path, 'r') as json_file:
            updated_metadata = json.load(json_file)
        print(updated_metadata)
        return jsonify(updated_metadata), 200

    return jsonify(updated_metadata), 200

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        users = load_users()
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Check if the email exists and the password is correct
        if email not in users or users[email]['password'] != password:
            return jsonify({"message": "Invalid email or password."}), 401

        user_level = users[email]['level']  # Get the user's level
        return jsonify({"message": "Login successful.", "level": user_level}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    try:
        users = load_users()
        data = request.json
        email = data.get('email')
        password = data.get('password')
        level = data.get('level', 'User')  # Default to 'Standard' if not provided

        # Check if the user already exists
        if email in users:
            return jsonify({"message": "User already exists."}), 400

        # Register the new user with their password and level
        users[email] = {"password": password, "level": level}
        save_users(users)

        return jsonify({"message": "Registration successful."}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Threat monitoring data endpoint
def get_threat_monitoring_data():
    # Path to the uploads folder
    uploads_folder = THREAT_FOLDER
    threats = []  # List to hold threats that match the criteria

    # Traverse the uploads folder
    for filename in os.listdir(uploads_folder):
        if filename.endswith('.json'):  # Check for JSON files
            json_file_path = os.path.join(uploads_folder, filename)

            try:
                with open(json_file_path, 'r') as json_file:
                    metadata = json.load(json_file)  # Load the JSON data

                    # Check the conditions: threat_score > 50 or is_synthetic is True
                    threat_score = metadata.get('threat_score', 0)
                    is_synthetic = metadata.get('is_synthetic', False)
                    
                    if threat_score > 50 or is_synthetic:
                        threat_info = {
                            'filename': filename,
                            'user_name': metadata.get('user_name', 'Unknown'),
                            'user_level': metadata.get('user_level', 'Unknown'),
                            'threat_score': threat_score,
                            'is_synthetic': is_synthetic
                        }
                        threats.append(threat_info)  # Add to the threats list
            except Exception as e:
                print(f"Error reading {json_file_path}: {e}")

    return threats  # Return the list of threats


@app.route('/threat-monitoring', methods=['GET'])
def threat_monitoring():
    threats = get_threat_monitoring_data()  # Get the threats
    print(threats)
    return jsonify(threats), 200  # Return as JSON response

# Utility function to load users from a JSON file
def load_users():
    if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error: JSON file is invalid, initializing as empty dictionary.")
            return {}
    return {}

# Utility function to save users to a JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
