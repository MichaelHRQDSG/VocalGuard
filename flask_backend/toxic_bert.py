import os
import json
import re
from detoxify import Detoxify

# 设置模型缓存路径
os.environ['TRANSFORMERS_CACHE'] = '/data/HRQ/VocalGuard/VocalGuard/flask_backend/toxic_bert_model'

# 初始化 Detoxify 模型
detoxify_model = Detoxify('original')
path_config_file = 'url_metadata.json'
try:
    with open(path_config_file, 'r', encoding='utf-8') as config_file:
        paths = json.load(config_file)
        input_json_path = paths.get("input_json_path", "").strip()
        output_json_path = paths.get("output_json_path", "").strip()
        
        if not input_json_path or not output_json_path:
            raise ValueError("Missing 'input_json_path' or 'output_json_path' in the config file.")
except Exception as e:
    print(f"Error reading path configuration: {e}")
    exit(1)

# 读取 JSON 文件
with open(input_json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 假设 JSON 文件的内容为 {"text": "A large block of text ..."}
text = data.get("text", "")

# 使用正则表达式拆分大段文字为句子
# 匹配句末标点（. ! ?）加空格或结束符号
sentences = re.split(r'(?<=[.!?])\s+', text)

# 存储符合条件的结果
filtered_results = []

# 遍历每一句话，检测毒性
for idx, sentence in enumerate(sentences):
    results = detoxify_model.predict(sentence)
    
    # 检查是否有任何毒性类别得分超过 0.5
    for toxic_category, score in results.items():
        if score > 0.5:
            # 如果超过阈值，记录句序号、句内容、毒性类别和得分
            filtered_results.append({
                "index": idx,
                "sentence": sentence.strip(),
                "toxic_category": toxic_category,
                "score": round(score, 5)
            })

# 将结果写入 JSON 文件
with open(output_json_path, 'w', encoding='utf-8') as file:
    json.dump(filtered_results, file, ensure_ascii=False, indent=4)

print(f"Filtered toxic sentences saved to {output_json_path}")