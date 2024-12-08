import torch
import torchaudio
import numpy as np
import soundfile as sf
from transformers import Wav2Vec2FeatureExtractor, WavLMForXVector

# 设置设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载预训练的模型和特征提取器
local_model_path = "./WavLM/wavlm_sv_model"  # 替换为你保存模型文件的本地路径
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(local_model_path)
model = WavLMForXVector.from_pretrained(local_model_path).to(device)
model.eval()

# 定义音频预处理函数
def preprocess_audio(audio_path, target_sample_rate=16000):
    """
    预处理音频，将音频文件读取并重采样到目标采样率
    """
    # 使用 soundfile 读取音频
    waveform, sample_rate = sf.read(audio_path)
    
    # 如果是多声道，转换为单声道
    if len(waveform.shape) > 1:
        waveform = np.mean(waveform, axis=1)
    
    # 如果采样率不符合，进行重采样
    if sample_rate != target_sample_rate:
        waveform = torch.from_numpy(waveform).float()
        waveform = torchaudio.functional.resample(waveform, sample_rate, target_sample_rate)
        waveform = waveform.numpy()
    
    # 转换为 torch.Tensor
    waveform = torch.from_numpy(waveform).float()
    
    return waveform

# 提取说话人嵌入的函数
def extract_embedding(waveform):
    """
    提取音频的嵌入特征
    """
    waveform = waveform.to(device)
    
    # 将音频转换为输入张量，并确保形状为 [batch_size, sequence_length]
    inputs = feature_extractor(waveform, sampling_rate=16000, padding=False, return_tensors="pt").to(device)
    inputs['input_values'] = inputs['input_values'].squeeze(-1)  # 移除多余的维度

    with torch.no_grad():
        # 提取音频嵌入特征
        embeddings = model(**inputs).embeddings
        # 对时间维度取平均值，得到固定长度的嵌入
        embedding = torch.mean(embeddings, dim=0).cpu().numpy()
    
    return embedding
