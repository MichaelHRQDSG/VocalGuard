import torch
import torchaudio
import numpy as np
import os
from models.AASIST import Model  # 假设已存在的模型加载器



# 预处理音频数据，确保音频为 mono-channel 且采样率为 16kHz
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

# 从视频中提取音频
def extract_audio_from_video(video_path, output_audio_path='extracted_audio.wav'):
    import moviepy.editor as mp
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    return output_audio_path

# 预处理音频数据
def detect_synthetic_audio(model, audio_path, device, config):
    """
    检测音频是否为合成音频。
    
    参数:
    - model: 训练好的模型
    - audio_path: 输入音频的路径
    - device: 用于推理的设备 (CPU/GPU)
    - config: 模型的配置文件
    
    返回:
    - 检测结果（合成音频或真实音频）
    """
    # 预处理音频
    waveform = preprocess_audio(audio_path, target_sample_rate=16000, nb_samp=config['model_config']['nb_samp'])
    
    # 打印音频的维度
    print(f"音频输入维度: {waveform.shape}")
    
    # 扩展音频维度，使其符合模型的输入要求
    inputs = waveform.unsqueeze(0).to(device)  # [1, num_channels, num_samples]
    
    # 使用模型推理
    with torch.no_grad():
        # 根据模型的forward函数，返回两个输出：last_hidden和output
        last_hidden, output = model(inputs)
    
    # 打印模型输出的形状
    print(f"模型输出的形状: {output.shape}")
    
    # 获取模型输出的softmax值作为概率
    probabilities = torch.softmax(output, dim=1)
    
    # 选择代表“合成音频”的概率（第二个类别，索引为1）
    prob_synthetic = probabilities[0][1].item()
    
    # 返回检测结果
    if prob_synthetic > 0.5:
        return f"音频 {audio_path} 被检测为合成音频 (probability: {prob_synthetic:.2f})"
    else:
        return f"音频 {audio_path} 被检测为真实音频 (probability: {prob_synthetic:.2f})"



# 加载模型
def load_aasist_model(model_path, config, device):
    model = Model(config['model_config'])  # 使用配置文件初始化模型
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint)
    model = model.to(device)  # 确保模型在指定的设备上
    model.eval()
    return model

# 检测音频是否为合成音频
# 检测音频是否为合成音频
def detect_synthetic_audio(model, audio_path, device, config):
    # 预处理音频
    waveform = preprocess_audio(audio_path, target_sample_rate=16000, nb_samp=config['model_config']['nb_samp'])
    
    # 打印音频的维度
    print(f"音频输入维度: {waveform.shape}")
    
    # 准备模型输入
    inputs = waveform.to(device)  # 确保输入也在指定的设备上，输入为 [num_channels, num_samples] 或 [batch_size, num_channels, num_samples]
    
    # 使用模型推理
    with torch.no_grad():
        output = model(inputs)
    
    # If the output is a tuple, extract the first element
    if isinstance(output, tuple):
        output = output[0]
    
    # 打印模型输出的形状
    print(f"模型输出的形状: {output.shape}")
    
    # 计算输出张量的平均值，获取合成音频的概率
    prob = torch.sigmoid(output).mean().item()
    #prob = torch.sigmoid(output[0][0]).item()
    
    # Return detection result based on the probability
    if prob > 0.5:
        return f"音频 {audio_path} 被检测为合成音频 (probability: {prob:.2f})"
    else:
        return f"音频 {audio_path} 被检测为真实音频 (probability: {prob:.2f})"


def process_audio_files_in_directory(model, directory_path, device, config, output_file):
    # 打开输出文件
    with open(output_file, 'w') as f_out:
        # 遍历文件夹中的所有wav文件
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".wav"):
                    file_path = os.path.join(root, file)
                    # 检测音频是否为合成音频
                    result = detect_synthetic_audio(model, file_path, device, config)
                    # 将结果写入txt文件
                    f_out.write(result + '\n')
                    print(f"已处理文件: {file_path}")

def main():
    config_path = './aasist/config/AASIST.conf'
    model_path = './aasist/models/weights/AASIST.pth'
    directory_path = './audio_files'  # 要遍历的文件夹
    output_file = './detection_results.txt'  # 输出结果文件
    
    # 读取配置文件
    import json
    with open(config_path, 'r') as f_json:
        config = json.load(f_json)
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 加载模型
    model = load_aasist_model(model_path, config, device)
    
    # 处理文件夹中的所有音频文件并输出结果
    process_audio_files_in_directory(model, directory_path, device, config, output_file)
    print(f"所有文件已处理，结果已保存至 {output_file}")

if __name__ == '__main__':
    main()
