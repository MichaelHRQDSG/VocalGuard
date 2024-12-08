import json
import os
from deepface import DeepFace

JSON_FILE = 're_verify.json'  # Define your JSON file path
USER_FOLDER = 'user_folder'  # Define your base user folder path

def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def save_json(filepath, data):
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def get_user_image_path(username):
    # Construct the user image path and get the first image from the img folder
    user_img_folder = os.path.join(USER_FOLDER, username, 'imgs')
    if os.path.exists(user_img_folder):
        user_images = [f for f in os.listdir(user_img_folder) if os.path.isfile(os.path.join(user_img_folder, f))]
        if user_images:
            return os.path.join(user_img_folder, user_images[0])  # Return the first user image
    return None

def process_face_verification(username, user_data):
    temp_paths = [entry['temp_path'] for entry in user_data['images']]
    user_image_path = get_user_image_path(username)  # Get the first user image
    print(user_image_path)
    print(temp_paths)
    if not user_image_path:
        print(f"No user image found for {username}.")
        return False

    is_same_person = True
    emotions_detected = set()

    for temp_path in temp_paths:
        # Face verification using DeepFace
        try:
            result = DeepFace.verify(img1_path=temp_path, img2_path=user_image_path, model_name='VGG-Face')
            print("result1:", result)
            if not result['verified']:
                is_same_person = False
        except Exception as e:
            print(f"Error during face verification: {e}")
            is_same_person = False

        # Emotion analysis using DeepFace
        try:
            emotion_result = DeepFace.analyze(img_path=temp_path, actions=['emotion'])
            print("result2:", emotion_result)
            dominant_emotion = emotion_result[0]['dominant_emotion']
            print("result_do:", dominant_emotion)
            emotions_detected.add(dominant_emotion)
        except Exception as e:
            print(f"Error during emotion analysis: {e}")

    # Check if the detected emotions contain 'neutral' and 'happy'
    required_emotions = {'neutral', 'happy'}
    missing_emotions = required_emotions - emotions_detected
    emotions_matched = not missing_emotions

    # Determine the verification result and reason
    verification_result = is_same_person and emotions_matched
    reason = "good" if verification_result else f"Missing emotions: {', '.join(missing_emotions)}"

    # Write the result and reason back to the JSON file
    data = load_json(JSON_FILE)
    if username not in data:
        data[username] = {}
    data[username]['verification_result'] = verification_result
    data[username]['reason'] = reason
    save_json(JSON_FILE, data)

    return verification_result

if __name__ == "__main__":
    data = load_json(JSON_FILE)
    if data:
        # Extract the first key as the username
        username = list(data.keys())[0]
        print(f"Processing for username: {username}")
        result = process_face_verification(username, data[username])
        print(f"Verification result for {username}: {result}")
