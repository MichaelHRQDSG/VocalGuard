import os
import re
import requests
import json
from pydub import AudioSegment
import random

# Configuration
db_folder = './DB'  # Path to the DB folder containing subfolders with user audio files
text_folder = '../text_source/chinese'  # Path to the text source folder containing .txt files
url = "http://127.0.0.1:8020/tts_to_file"  # XTTS API URL

# Ensure directory exists
def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Get a list of .wav files in a directory
def get_wav_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.wav')]

# Get reference audio file for speaker
def get_reference_audio(wav_files, speaker_folder):
    if not wav_files:
        return None
    reference_file = random.choice(wav_files)  # Randomly choose a file as reference
    reference_path = os.path.join(speaker_folder, reference_file)
    audio = AudioSegment.from_file(reference_path)
    reference_audio = audio[:12 * 1000]  # Use up to the first 15 seconds
    temp_reference_name = os.path.splitext(reference_file)[0] + ".wav"  # Ensure unique name
    temp_reference_path = os.path.join(speaker_folder, temp_reference_name)
    reference_audio.export(temp_reference_path, format="wav")
    return temp_reference_path

# Generate synthetic audio
def generate_audio(text, speaker_id, content_id, sentence_id, speaker_wav_path, output_folder):
    output_file_path = os.path.join(output_folder, f"{speaker_id}_{content_id}_{sentence_id}.wav")
    data = {
        "text": text,
        "speaker_wav": speaker_wav_path,
        "language": "zh-cn",
        "file_name_or_path": output_file_path
    }
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        return output_file_path
    else:
        print(f"Failed to generate audio for {speaker_id}: {response.text}")
        return None

# Split sentences (you should define your own implementation)
def split_sentences(text):
    # Example implementation of splitting by common punctuation marks
    return re.split(r'[。！？]', text)

# Main processing function
def process_speakers():
    for speaker_id in os.listdir(db_folder):
        speaker_folder = os.path.join(db_folder, speaker_id)
        if not os.path.isdir(speaker_folder):
            continue
        
        wav_files = get_wav_files(speaker_folder)
        if len(wav_files) >= 60:
            print(f"Speaker {speaker_id} already has 60 or more files.")
            continue
        
        # Get reference audio
        reference_wav = get_reference_audio(wav_files, speaker_folder)
        if not reference_wav:
            print(f"No reference audio available for {speaker_id}. Skipping.")
            continue
        
        # Read and process text files
        sentence_count = len(wav_files) + 1
        for filename in os.listdir(text_folder):
            if filename.endswith(".txt"):
                content_id = os.path.splitext(filename)[0]
                file_path = os.path.join(text_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    for line_id, line in enumerate(lines, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        match = re.search(r'^(.*?)\s*\[标签：(.*?)\]$', line)
                        if match:
                            text = match.group(1).strip()
                            text = text.replace('"', '')
                            parts = split_sentences(text)  # Split text into sentences
                            combined_audio = AudioSegment.empty()  # Initialize empty audio segment
                            
                            for part_id, part in enumerate(parts, start=1):
                                part_audio_path = generate_audio(part, speaker_id, content_id, f"{line_id}_{part_id}", reference_wav, speaker_folder)
                                if part_audio_path:
                                    try:
                                        part_audio = AudioSegment.from_wav(part_audio_path)
                                        combined_audio += part_audio
                                        os.remove(part_audio_path)  # Remove part audio file
                                    except Exception as e:
                                        print(f"Error loading or deleting part audio {part_audio_path}: {e}")
                            
                            # Save combined audio
                            final_output_path = os.path.join(speaker_folder, f"{speaker_id}_{content_id}_{line_id}_combined.wav")
                            combined_audio.export(final_output_path, format="wav")
                            print(f"Combined audio saved as {final_output_path}")

                            sentence_count += 1
                            if sentence_count > 60:
                                break
                if sentence_count > 60:
                    break

# Run the main function
process_speakers()
