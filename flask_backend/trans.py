# import os
# import glob
# import whisper
# import json
# from tqdm import tqdm

# # 加载Whisper模型从本地路径
# local_model_path = "./local_whisper_model"  # 替换为你保存模型文件的路径
# model = whisper.load_model('medium',download_root=local_model_path).to("cuda")

# def transcribe_audio(audio_path, language="en"):
#     # 加载和处理音频文件
#     audio = whisper.load_audio(audio_path)
#     audio = whisper.pad_or_trim(audio)

#     # 生成log-Mel spectrogram
#     mel = whisper.log_mel_spectrogram(audio).to(model.device)

#     # 检测语言
#     _, probs = model.detect_language(mel)
#     print(f"Detected language: {max(probs, key=probs.get)}")

#     # 解码音频
#     options = whisper.DecodingOptions(language=language)
#     result = model.decode(mel, options)
#     return result.text

# def update_metadata(json_path, transcription):
#     """
#     更新与查询音频路径相对应的JSON文件的内容
#     """
#     with open(json_path, 'r') as f:
#         metadata = json.load(f)
    
#     metadata["is_specified_speaker"] = True  # Example change, adjust logic as needed
#     metadata["transcription"] = transcription
#     metadata["detection_context"]["completed"] = True

    
#     with open(json_path, 'w') as f:
#         json.dump(metadata, f, indent=4, ensure_ascii=False)
#     print(f"Metadata updated for {json_path}")

# def transcribe_from_metadata(metadata_path):
#     """
#     从metadata.json文件中获取音频路径并进行转录
#     """
#     # 读取metadata.json获取音频路径
#     with open(metadata_path, 'r') as f:
#         metadata = json.load(f)
    
#     audio_path = metadata["storage_path"]
#     if not os.path.exists(audio_path):
#         print(f"Audio file {audio_path} not found. Skipping.")
#         return
    
#     # 获取与音频文件同路径、同名的JSON文件路径
#     json_path = os.path.splitext(audio_path)[0] + '.json'
    
#     # 检查是否需要跳过已存在的转录
#     if "transcription" in metadata and metadata["transcription"]:
#         print(f"Skipping already transcribed audio file: {audio_path}")
#         return
    
#     print(f"Transcribing audio file: {audio_path}")
#     transcription = transcribe_audio(audio_path, language="en")
    
#     # 更新JSON文件
#     update_metadata(json_path, transcription)

# if __name__ == "__main__":
#     # 修改为你的metadata.json文件路径
#     metadata_path = "./metadata.json"
#     transcribe_from_metadata(metadata_path)
import os
import whisper
import json
from tqdm import tqdm

# 加载Whisper模型从本地路径
local_model_path = "./local_whisper_model"  # 替换为你保存模型文件的路径
model = whisper.load_model('medium', download_root=local_model_path).to("cuda")

def transcribe_audio(audio_path):
    """
    Transcribe audio and detect language using Whisper.
    """
    # 加载和处理音频文件
    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)

    # 生成log-Mel spectrogram
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # 检测语言
    detected_language, probs = model.detect_language(mel)
    language = max(probs, key=probs.get)
    print(f"Detected language: {language}")

    # 解码音频
    options = whisper.DecodingOptions(language=language)
    result = model.decode(mel, options)
    return result.text, language

def update_metadata(json_path, transcription, language):
    """
    更新与查询音频路径相对应的JSON文件的内容
    """
    with open(json_path, 'r') as f:
        metadata = json.load(f)

    metadata["is_specified_speaker"] = True  # 示例更新，可以根据实际需求调整逻辑
    metadata["transcription"] = transcription
    metadata["detected_language"] = language  # 添加检测到的语言
    metadata["detection_context"]["completed"] = True

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadata updated for {json_path}")

def transcribe_from_metadata(metadata_path):
    """
    从metadata.json文件中获取音频路径并进行转录和语言检测
    """
    # 读取metadata.json获取音频路径
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    audio_path = metadata["storage_path"]
    if not os.path.exists(audio_path):
        print(f"Audio file {audio_path} not found. Skipping.")
        return

    # 获取与音频文件同路径、同名的JSON文件路径
    json_path = os.path.splitext(audio_path)[0] + '.json'

    # 检查是否需要跳过已存在的转录
    if "transcription" in metadata and metadata["transcription"]:
        print(f"Skipping already transcribed audio file: {audio_path}")
        return

    print(f"Transcribing audio file: {audio_path}")
    transcription, language = transcribe_audio(audio_path)

    # 更新JSON文件
    update_metadata(json_path, transcription, language)

if __name__ == "__main__":
    # 修改为你的metadata.json文件路径
    metadata_path = "./metadata.json"
    transcribe_from_metadata(metadata_path)