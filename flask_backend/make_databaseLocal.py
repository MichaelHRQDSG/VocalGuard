import os
import faiss
import numpy as np
import torch
import pickle
import random
from tqdm import tqdm
import soundfile as sf
from transformers import Wav2Vec2FeatureExtractor, WavLMForXVector

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load pre-trained model and feature extractor
local_model_path = "./WavLM/wavlm_sv_model"  # Replace with the path to your saved model files
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(local_model_path)
model = WavLMForXVector.from_pretrained(local_model_path).to(device)

def extract_feature(waveform, path=None):
    """
    Extract audio features. If cached, load directly; otherwise, compute and cache.
    """
    cache_path = path.replace('.wav', '-sv.pt') if path else None
    if cache_path and os.path.exists(cache_path):
        return torch.load(cache_path, map_location=device)
    
    print("Original waveform shape:", waveform.shape)
    
    # Adjust waveform shape to ensure it is [sequence_length]
    if waveform.ndim == 3 and waveform.shape[0] == 1:
        waveform = waveform.squeeze()
    elif waveform.ndim == 3:
        waveform = waveform.squeeze(-1)
    elif waveform.ndim > 1:
        waveform = waveform.flatten()
    
    if waveform.ndim != 1:
        raise ValueError(f"Expected 1D waveform input, got shape {waveform.shape}")

    print("Adjusted waveform shape:", waveform.shape)
    
    inputs = feature_extractor(waveform, sampling_rate=16000, padding=False, return_tensors="pt").to(device)
    print("Feature extractor input shape:", inputs['input_values'].shape)
    
    with torch.no_grad():
        embeddings = model(**inputs).embeddings
        embeddings = torch.mean(embeddings, dim=0).cpu()  # Move embeddings to CPU
        if cache_path:
            torch.save(embeddings, cache_path)
        print("Embeddings shape:", embeddings.shape)
    return embeddings

def merge_speaker_embeddings(speaker_id, audio_paths, duration_limit=10):
    """
    Merge audio for the same speaker, extract features, and compute the average.
    duration_limit: Limits processing duration per audio clip to 10 seconds.
    """
    embeddings = []
    max_samples = 150  # Limit to 150 audio samples per speaker
    audio_paths = random.sample(audio_paths, min(len(audio_paths), max_samples))

    for path in audio_paths:
        waveform, sr = sf.read(path, dtype='float32')
        
        # Convert stereo (2 channels) to mono by averaging channels
        if waveform.ndim == 2 and waveform.shape[1] == 2:
            waveform = np.mean(waveform, axis=1)
        
        num_samples_limit = int(sr * duration_limit)
        if waveform.shape[0] > num_samples_limit:
            waveform = waveform[:num_samples_limit]
        
        waveform = torch.tensor(waveform).unsqueeze(0)
        embedding = extract_feature(waveform, path)
        embeddings.append(embedding)
    
    if embeddings:
        embeddings = [embedding.cpu() for embedding in embeddings]  # Move all embeddings to CPU
        embeddings = torch.stack(embeddings)
        avg_embedding = torch.mean(embeddings, dim=0)
        print(avg_embedding.shape)
        return avg_embedding
    return None


def build_speaker_database(database_dir, index_path, speaker_ids_path):
    """
    Build speaker database, generate FAISS index, and save speaker ID list.
    """
    speaker_embeddings = []
    speaker_ids = []
    res = faiss.StandardGpuResources()  # Initialize GPU resources

    speaker_dirs = [d for d in os.listdir(database_dir) if os.path.isdir(os.path.join(database_dir, d))]
    print(f"Found {len(speaker_dirs)} speakers.")

    for speaker_id in tqdm(speaker_dirs):
        speaker_dir = os.path.join(database_dir, speaker_id)
        audio_files = [f for f in os.listdir(speaker_dir) if f.endswith('.wav') or f.endswith('.flac')]
        audio_paths = [os.path.join(speaker_dir, f) for f in audio_files]

        avg_embedding = merge_speaker_embeddings(speaker_id, audio_paths)
        if avg_embedding is not None:
            speaker_embeddings.append(avg_embedding.cpu())  # Ensure embedding is on CPU
            speaker_ids.append(speaker_id)
            print(f"Processed speaker {speaker_id}, number of audio files: {len(audio_paths)}")
        else:
            print(f"Speaker {speaker_id} has no valid audio files, skipped.")
    
    speaker_ids = np.array(speaker_ids)

    # Stack embeddings and convert to NumPy array
    embeddings = torch.stack(speaker_embeddings).numpy()
    print(f"Initial Embeddings shape: {embeddings.shape}")

    # Ensure embeddings are at least 2D
    embeddings = np.atleast_2d(embeddings)
    print(f"Shape after ensuring 2D: {embeddings.shape}")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(speaker_ids_path, 'wb') as f:
        pickle.dump(speaker_ids, f)
    print(f"Index saved to {index_path}")
    print(f"Speaker ID list saved to {speaker_ids_path}")

if __name__ == "__main__":
    database_dir = "DB"
    index_path = "./DB/speaker_index.faiss"
    speaker_ids_path = "./DB/speaker_ids.pkl"
    build_speaker_database(database_dir, index_path, speaker_ids_path)




def build_speaker_database(database_dir, index_path, speaker_ids_path):
    """
    Build speaker database, generate FAISS index, and save speaker ID list.
    """
    speaker_embeddings = []
    speaker_ids = []
    res = faiss.StandardGpuResources()  # Initialize GPU resources

    speaker_dirs = [d for d in os.listdir(database_dir) if os.path.isdir(os.path.join(database_dir, d))]
    print(f"Found {len(speaker_dirs)} speakers.")

    for speaker_id in tqdm(speaker_dirs):
        speaker_dir = os.path.join(database_dir, speaker_id)
        audio_files = [f for f in os.listdir(speaker_dir) if f.endswith('.wav') or f.endswith('.flac')]
        audio_paths = [os.path.join(speaker_dir, f) for f in audio_files]

        avg_embedding = merge_speaker_embeddings(speaker_id, audio_paths)
        if avg_embedding is not None:
            speaker_embeddings.append(avg_embedding.cpu())  # Ensure embedding is on CPU
            speaker_ids.append(speaker_id)
            print(f"Processed speaker {speaker_id}, number of audio files: {len(audio_paths)}")
        else:
            print(f"Speaker {speaker_id} has no valid audio files, skipped.")
    
    speaker_ids = np.array(speaker_ids)

    # Stack embeddings and convert to NumPy array
    embeddings = torch.stack(speaker_embeddings).numpy()
    print(f"Initial Embeddings shape: {embeddings.shape}")

    # Ensure embeddings are at least 2D
    embeddings = np.atleast_2d(embeddings)
    print(f"Shape after ensuring 2D: {embeddings.shape}")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(speaker_ids_path, 'wb') as f:
        pickle.dump(speaker_ids, f)
    print(f"Index saved to {index_path}")
    print(f"Speaker ID list saved to {speaker_ids_path}")

if __name__ == "__main__":
    database_dir = "DB"
    index_path = "./DB/speaker_index.faiss"
    speaker_ids_path = "./DB/speaker_ids.pkl"
    build_speaker_database(database_dir, index_path, speaker_ids_path)
