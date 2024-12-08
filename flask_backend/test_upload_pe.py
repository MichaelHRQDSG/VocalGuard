import requests
import base64

# Function to convert a file to a base64 string
def file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            # Ensure proper padding
            if len(encoded_string) % 4 != 0:
                encoded_string += '=' * (4 - len(encoded_string) % 4)
            return encoded_string
    except Exception as e:
        print(f"Error encoding file {file_path}: {e}")
        return None

# Prepare the test data
profile_photo_path = '/data/HRQ/VocalGuard/VocalGuard/frontend/app/public/imgs/art1.jpg'  # Replace with the path to your test image
audio_file_path = '/data/HRQ/VocalGuard/VocalGuard/audio_files/1.wav'  # Replace with the path to your test audio file

# Convert files to base64
profile_photo_base64 = file_to_base64(profile_photo_path)
audio_info_base64 = file_to_base64(audio_file_path)

if not profile_photo_base64 or not audio_info_base64:
    print("Error: One or both files could not be encoded.")
else:
    # Prepare the data in the required format
    data = {
        "userInfo": {
            "name": "John Doe",
            "level": "User"
        },
        "profilePhoto": f"data:image/jpeg;base64,{profile_photo_base64}",
        "audioInfo": f"data:audio/mp3;base64,{audio_info_base64}",
        "personalIntro": "This is my personal introduction."
    }

    # Send the POST request to the backend
    try:
        print("Sending request to the backend...")
        response = requests.post('http://127.0.0.1:5000/upload-personal-info', json=data)

        # Print the response
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
