import torch
import torchaudio
import json
import os
import subprocess
from aasist.models.AASIST import Model  # Assuming an existing model loader

# Preprocess audio data to ensure mono-channel and a sample rate of 16kHz
def preprocess_audio(audio_path, target_sample_rate=16000, nb_samp=64600):
    try:
        # Load the audio file
        waveform, sample_rate = torchaudio.load(audio_path)

        # Ensure audio was loaded properly
        if waveform is None or waveform.size(0) == 0:
            raise ValueError(f"Error loading audio file: {audio_path}")

        # Resample the audio if needed
        if sample_rate != target_sample_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
            waveform = resampler(waveform)

        # Convert multi-channel to mono
        if waveform.size(0) > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # Trim or pad the audio to the specified length
        if waveform.size(1) > nb_samp:
            waveform = waveform[:, :nb_samp]
        elif waveform.size(1) < nb_samp:
            padding = nb_samp - waveform.size(1)
            waveform = torch.nn.functional.pad(waveform, (0, padding))

        return waveform  # Ensure it's properly returned

    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

# Load the AASIST model
def load_aasist_model(model_path, config, device):
    model = Model(config['model_config'])  # Initialize the model using the config
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint)
    model = model.to(device)
    model.eval()
    return model

# Detect if audio is synthetic
def detect_synthetic_audio(model, audio_path, device, config):
    # Preprocess audio
    waveform = preprocess_audio(audio_path, target_sample_rate=16000, nb_samp=config['model_config']['nb_samp'])

    # Ensure waveform is processed
    if waveform is None:
        return None

    print(f"Audio input shape: {waveform.shape}")

    # Prepare model input
    inputs = waveform.to(device)

    # Perform inference
    with torch.no_grad():
        _, output = model(inputs)
        probabilities = torch.sigmoid(output).data.cpu().numpy().ravel()

    # Extract probability for synthetic detection
    probability = float(probabilities[1]) if probabilities.size > 0 else 0.0  # Convert to standard float
    print(f"Probabilities: {probabilities}")

    # Determine if the audio is synthetic
    is_synthetic = probability <= 0.4
    print(audio_path)
    # Run deepfake.py using subprocess and capture the output

    result = {
        "is_synthetic": bool(is_synthetic),  # Convert to a standard Python boolean
        "probability": round(probability, 2),  # Convert to standard float
        "deepfake_analysis": probability
    }
    print(result)
    return result

def perform_audio_analysis(config_path, model_path, metadata_path):
    # Load config
    with open(config_path, 'r') as f_json:
        config = json.load(f_json)

    # Load audio file path from the metadata
    with open(metadata_path, 'r') as metadata_file:
        metadata = json.load(metadata_file)
    
    audio_path = metadata.get('storage_path')
    
    if not audio_path or not os.path.exists(audio_path):
        print("Audio path not found or file does not exist.")
        return

    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load model
    model = load_aasist_model(model_path, config, device)

    # Perform detection
    result = detect_synthetic_audio(model, audio_path, device, config)

    if result:
        # Determine JSON file path based on the audio file path
        json_file_path = os.path.splitext(audio_path)[0] + '.json'
        
        # Load existing metadata from the JSON file
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                audio_metadata = json.load(json_file)
        else:
            print(f"JSON metadata file {json_file_path} not found. Creating a new one.")
            audio_metadata = {}

        # Update fields in the metadata
        audio_metadata['is_synthetic'] = result['is_synthetic']
        audio_metadata['deepfake'] = {
            "completed": True,
            "result": {"confidence": result['probability']}
        }

        # Save updated metadata back to the JSON file
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(audio_metadata, json_file, indent=4)
        print(f"Result saved to {json_file_path}")
    else:
        print("Failed to process the audio.")

# Expose variables for external use
config_path = './aasist/config/AASIST.conf'
model_path = './aasist/models/weights/AASIST.pth'
metadata_path = './metadata.json'  # Path to the metadata file containing the audio path

# Example usage
if __name__ == '__main__':
    perform_audio_analysis(config_path, model_path, metadata_path)
