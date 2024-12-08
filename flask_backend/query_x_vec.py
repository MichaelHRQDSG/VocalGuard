# import torch
# import torchaudio
# from speechbrain.pretrained import EncoderClassifier
# import numpy as np
# import os
# import pickle
# import json

# def load_audio(audio_path):
#     """
#     Load an audio file and convert it to the required waveform format.
#     """
#     waveform, sample_rate = torchaudio.load(audio_path)
#     if sample_rate != 16000:
#         waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)
#     return waveform

# def cosine_similarity(embedding1, embedding2):
#     """
#     Calculate cosine similarity between two embeddings.
#     """
#     return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

# # Load pre-trained ECAPA-TDNN model from SpeechBrain
# classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa")

# def extract_embedding(audio_path):
#     """
#     Extract speaker embedding using ECAPA-TDNN model from SpeechBrain.
#     """
#     waveform = load_audio(audio_path)
#     with torch.no_grad():
#         embeddings = classifier.encode_batch(waveform).squeeze().detach().cpu().numpy()
#         if embeddings.ndim == 2:
#             embeddings = embeddings[0]
#     return embeddings

# def save_embeddings(dataset_path):
#     """
#     Extract and save embeddings for each speaker in their respective directories.
#     """
#     for root, _, files in os.walk(dataset_path):
#         speaker_id = os.path.basename(root)  # Assuming root directory name is speaker ID
#         embeddings_list = []

#         for file in files:
#             if file.endswith(".wav"):
#                 audio_path = os.path.join(root, file)
#                 embedding = extract_embedding(audio_path)
#                 embeddings_list.append(embedding)

#         if embeddings_list:
#             # Calculate the average embedding
#             avg_embedding = np.mean(embeddings_list, axis=0)
#             # Save the average embedding to the speaker's directory
#             embedding_file = os.path.join(root, f"{speaker_id}_avg_embedding.pkl")
#             if not os.path.exists(embedding_file):  # Check if the file already exists
#                 with open(embedding_file, 'wb') as f:
#                     pickle.dump(avg_embedding, f)
#             else:
#                 print(f"Embedding file {embedding_file} already exists, skipping.")

# def get_audio_path_from_metadata(metadata_path):
#     """
#     从metadata.json文件中获取音频路径
#     """
#     with open(metadata_path, 'r') as f:
#         metadata = json.load(f)
#     return metadata["storage_path"]

# def update_metadata(json_path, matched_speaker, similarity):
#     """
#     更新与查询音频路径相对应的JSON文件的内容
#     """
#     print(json_path)
#     with open(json_path, 'r', encoding='utf-8') as f:
#         metadata = json.load(f)
    
#     similarity = float(similarity)  # Convert to float for JSON compatibility
    
#     metadata["is_specified_speaker"] = True if similarity >= 0.6 else False
#     metadata["speaker_id"] = matched_speaker if matched_speaker else None
#     metadata["query_speakers"]["completed"] = True
#     metadata["query_speakers"]["result"] = {"similarity": similarity}
    
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(metadata, f, indent=4, ensure_ascii=False)
#     print(f"Metadata updated for {json_path}")

# def match_speaker(audio_path, dataset_path,query_audio_path):
#     """
#     Match a new audio file to a speaker using cosine similarity with stored embeddings.
#     """
#     json_path = os.path.splitext(query_audio_path)[0] + '.json'
#     query_embedding = extract_embedding(audio_path)

#     best_match = None
#     best_similarity = -1  # Initialize with lowest possible similarity

#     # Traverse dataset to find the best match
#     for root, _, files in os.walk(dataset_path):
#         for file in files:
#             if file.endswith("_avg_embedding.pkl"):
#                 embedding_path = os.path.join(root, file)
#                 with open(embedding_path, 'rb') as f:
#                     stored_embedding = pickle.load(f)
#                     similarity = cosine_similarity(query_embedding, stored_embedding)
#                     if similarity > best_similarity:
#                         best_similarity = similarity
#                         best_match = os.path.basename(root)  # Get the speaker ID

#     # Check if the best similarity is below the threshold
#     if best_similarity < 0.6:
#         print("No matching speaker found.")
#         update_metadata(json_path, None, best_similarity)
#         return None, best_similarity

#     print(f"Best Match: {best_match}, Similarity: {best_similarity:.4f}")
#     update_metadata(json_path, best_match, best_similarity)
#     return best_match, best_similarity

# if __name__ == "__main__":
#     # 查询音频文件路径
#     metadata_path = "./metadata.json"  # 替换为你metadata.json的路径
#     query_audio_path = get_audio_path_from_metadata(metadata_path)
#     dataset_path = "DB"  # Path to your dataset
#     save_embeddings(dataset_path)
#     match_speaker(query_audio_path, dataset_path,query_audio_path)
import torch
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import numpy as np
import os
import pickle
import json

def load_audio(audio_path):
    """
    Load an audio file and convert it to the required waveform format.
    """
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)
    return waveform

def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings.
    """
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

# Load pre-trained ECAPA-TDNN model from SpeechBrain
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa")

def extract_embedding(audio_path):
    """
    Extract speaker embedding using ECAPA-TDNN model from SpeechBrain.
    """
    waveform = load_audio(audio_path)
    with torch.no_grad():
        embeddings = classifier.encode_batch(waveform).squeeze().detach().cpu().numpy()
        if embeddings.ndim == 2:
            embeddings = embeddings[0]
    return embeddings

def save_embeddings_if_needed(dataset_path):
    """
    Extract and save embeddings for each speaker in their respective directories if not already existing.
    """
    for root, _, files in os.walk(dataset_path):
        speaker_id = os.path.basename(root)  # Assuming root directory name is speaker ID
        embedding_file = os.path.join(root, f"{speaker_id}_avg_embedding.pkl")

        if os.path.exists(embedding_file):
            print(f"Embedding file {embedding_file} already exists, skipping.")
            continue

        embeddings_list = []
        for file in files:
            if file.endswith(".wav"):
                audio_path = os.path.join(root, file)
                embedding = extract_embedding(audio_path)
                embeddings_list.append(embedding)

        if embeddings_list:
            # Calculate the average embedding
            avg_embedding = np.mean(embeddings_list, axis=0)
            # Save the average embedding to the speaker's directory
            with open(embedding_file, 'wb') as f:
                pickle.dump(avg_embedding, f)

def get_audio_path_from_metadata(metadata_path):
    """
    从metadata.json文件中获取音频路径
    """
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata["storage_path"]

def update_metadata(json_path, matched_speaker, similarity):
    """
    更新与查询音频路径相对应的JSON文件的内容
    """
    print(json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    similarity = float(similarity)  # Convert to float for JSON compatibility
    
    metadata["is_specified_speaker"] = True if similarity >= 0.6 else False
    metadata["speaker_id"] = matched_speaker if matched_speaker else None
    metadata["query_speakers"] = {
        "completed": True,
        "result": {"similarity": similarity}
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadata updated for {json_path}")

def match_speaker(audio_path, dataset_path, query_audio_path):
    """
    Match a new audio file to a speaker using cosine similarity with stored embeddings.
    """
    json_path = os.path.splitext(query_audio_path)[0] + '.json'
    query_embedding = extract_embedding(audio_path)

    best_match = None
    best_similarity = -1  # Initialize with lowest possible similarity

    # Traverse dataset to find the best match
    for root, _, files in os.walk(dataset_path):
        for file in files:
            if file.endswith("_avg_embedding.pkl"):
                embedding_path = os.path.join(root, file)
                with open(embedding_path, 'rb') as f:
                    stored_embedding = pickle.load(f)
                    similarity = cosine_similarity(query_embedding, stored_embedding)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = os.path.basename(root)  # Get the speaker ID
    print(best_match)
    print(best_similarity)
    # Check if the best similarity is below the threshold
    if best_similarity < 0.5:
        print("No matching speaker found.")
        update_metadata(json_path, None, best_similarity)
        return None, best_similarity

    print(f"Best Match: {best_match}, Similarity: {best_similarity:.4f}")
    update_metadata(json_path, best_match, best_similarity)
    return best_match, best_similarity

if __name__ == "__main__":
    # 查询音频文件路径
    metadata_path = "./metadata.json"  # 替换为你metadata.json的路径
    query_audio_path = get_audio_path_from_metadata(metadata_path)
    dataset_path = "DB"  # Path to your dataset
    save_embeddings_if_needed(dataset_path)
    match_speaker(query_audio_path, dataset_path, query_audio_path)