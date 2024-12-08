import requests
import base64
import json

# Function to convert an audio file to a base64 string
def file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        return encoded_string

# Prepare the test data
audio_file_path = '/data/HRQ/VocalGuard/VocalGuard/audio_files/1.wav'  # Replace with the path to your audio file

# Convert the audio file to a base64 string
audio_base64 = file_to_base64(audio_file_path)

# Prepare the data in the required format
data = {
    "audioFile": f"data:audio/mp3;base64,{audio_base64}",
    "userInfo": {
        "name": "John Doe",
        "level": "User",
        "detection_info": False
    }
}

# Send the POST request to the backend
response = requests.post('http://127.0.0.1:5000/upload', json=data)

# Print the response
print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except json.JSONDecodeError:
    print("Response Text:", response.text)
