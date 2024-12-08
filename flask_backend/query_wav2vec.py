import faiss
import numpy as np
import pickle
import torch
import csv
import json
import os
from transformers import Wav2Vec2FeatureExtractor, WavLMForXVector
from speaker_recognition_utils import preprocess_audio

# 设置设备
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 加载预训练的模型和特征提取器
local_model_path = "./WavLM/wavlm_sv_model"  # 替换为你保存模型文件的本地路径
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(local_model_path)
model = WavLMForXVector.from_pretrained(local_model_path).to(device)

def cosine_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two vectors.
    """
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

def extract_embedding(waveform):
    """
    提取音频的嵌入特征
    """
    # 将音频转换为输入张量，并确保形状为 [batch_size, sequence_length]
    inputs = feature_extractor(waveform, sampling_rate=16000, padding=False, return_tensors="pt").to(device)
    inputs['input_values'] = inputs['input_values'].squeeze(-1)  # 移除多余的维度
    with torch.no_grad():
        embeddings = model(**inputs).embeddings
        embeddings = torch.mean(embeddings, dim=0).cpu().numpy()  # 获取平均值并返回为 NumPy 数组
    return embeddings

def update_metadata(json_path, matched_speaker, similarity):
    """
    更新与查询音频路径相对应的JSON文件的内容
    """
    print(json_path)
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    # Convert numpy.float32 to Python float for JSON serialization compatibility
    similarity = float(similarity)
    
    metadata["is_specified_speaker"] = True if similarity >= 0.6 else False
    metadata["speaker_id"] = matched_speaker if matched_speaker else None
    metadata["query_speakers"]["completed"] = True
    metadata["query_speakers"]["result"] = {"similarity": similarity}
    
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadata updated for {json_path}")

def get_audio_path_from_metadata(metadata_path):
    """
    从metadata.json文件中获取音频路径
    """
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata["storage_path"]

def find_all_speaker_similarities(query_audio_path, speaker_embeddings_path, speaker_ids_path, threshold=0.85):
    """
    Find cosine similarity between query audio and all speakers in the database, and update the corresponding JSON file.
    """
    json_path = os.path.splitext(query_audio_path)[0] + '.json'

    # Load speaker embeddings and IDs
    with open(speaker_embeddings_path, 'rb') as f:
        speaker_embeddings = pickle.load(f)
    with open(speaker_ids_path, 'rb') as f:
        speaker_ids = pickle.load(f)

    # Preprocess audio and extract embedding
    waveform = preprocess_audio(query_audio_path)
    query_embedding = extract_embedding(waveform)

    # Calculate cosine similarity with each speaker embedding
    similarities = [cosine_similarity(query_embedding, speaker_embedding) for speaker_embedding in speaker_embeddings]

    # Find the best match
    max_similarity = max(similarities)
    matched_speaker = speaker_ids[np.argmax(similarities)] if max_similarity >= threshold else None

    # Update JSON file
    update_metadata(json_path, matched_speaker, max_similarity)

    print(f"Similarity: {max_similarity:.4f}, Matched Speaker ID: {matched_speaker if matched_speaker else 'No match'}")

if __name__ == "__main__":
    # 查询音频文件路径
    metadata_path = "./metadata.json"  # 替换为你metadata.json的路径
    query_audio_path = get_audio_path_from_metadata(metadata_path)
    # 索引和说话人ID列表路径
    index_path = "./DB/speaker_index.faiss"
    speaker_ids_path = "./DB/speaker_ids.pkl"
    threshold = 0.6
    
    # 查找所有说话人的相似度并更新相关JSON文件
    find_all_speaker_similarities(query_audio_path, index_path, speaker_ids_path, threshold)
