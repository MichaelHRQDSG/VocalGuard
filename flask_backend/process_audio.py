import sys

def process_audio(audio_file):
    # 模拟处理音频文件
    result = f'Processed audio file: {audio_file}'
    
    # 写入结果到 result.txt 文件
    with open('result.txt', 'w') as f:
        f.write(result)

if __name__ == '__main__':
    audio_file = sys.argv[1]
    process_audio(audio_file)