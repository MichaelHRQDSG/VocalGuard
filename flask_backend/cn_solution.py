import json
import os
import re
import torch
from transformers import pipeline

class Llama3:
    def __init__(self, device) -> None:
        self.device = device
        self.pipeline = pipeline(
            "text-generation",
            model="akjindal53244/Llama-3.1-Storm-8B",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map=self.device,
        )

    def generate(self, prompt):
        outputs = self.pipeline(prompt, max_new_tokens=512, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
        print(outputs)
        return outputs[0]["generated_text"]

def clean_response(text):
    # 清理多余的空白符号、换行符以及无关字符
    cleaned_text = re.sub(r'\s+', ' ', text)  # 将多个空格和换行符压缩为单个空格
    return cleaned_text.strip()


def generate_department_solution(text, department_name, llama3_instance):
    # 为部门构建提示
    prompt = f"""
    现在有一个假音频检测结果：{text}:
    请使用中文回答，为本公司{department_name}部门提供具体的、可操作的解决方案，以应对这些情况。请仅提供答案，不要重复问题或检测结果。
    """
    try:
        solution_content = llama3_instance.generate(prompt).strip()
        solution_content = clean_response(solution_content)
        cutoff_point = solution_content.find("请仅提供答案，不要重复问题或检测结果。")
        if cutoff_point != -1:
            solution_content = solution_content[cutoff_point + len("请仅提供答案，不要重复问题或检测结果。"):].strip()
    except Exception as e:
        print(f"生成{department_name}的解决方案时出错: {str(e)}")
        solution_content = {
            "error": f"使用Llama3生成{department_name}的解决方案失败。",
            "details": str(e)
        }
    
    return solution_content

def generate_solutions(json_file_path, llama3_instance, threat_folder):
    # 从JSON文件加载检测结果
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        detection_results = json.load(json_file)

    # 为每个部门生成解决方案
    solutions = {
        "Legal_Department_Solution": generate_department_solution(detection_results, "法务部门", llama3_instance),
        "Technical_Department_Solution": generate_department_solution(detection_results, "技术部门", llama3_instance),
        "HR_Department_Solution": generate_department_solution(detection_results, "人事部门", llama3_instance)
    }

    # 确保威胁文件夹存在
    os.makedirs(threat_folder, exist_ok=True)

    # 准备要保存到JSON文件中的内容
    combined_content = {
        "original_json": detection_results,
        "department_solutions": solutions
    }

    # 将组合内容保存到威胁文件夹中的新JSON文件
    solution_file_path = os.path.join(threat_folder, os.path.basename(os.path.splitext(json_file_path)[0]) + '_solution.json')
    with open(solution_file_path, 'w', encoding='utf-8') as solution_file:
        json.dump(combined_content, solution_file, indent=4, ensure_ascii=False)

    print(f"解决方案已生成并保存到 {solution_file_path}.")
    return solution_file_path

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    llama3_instance = Llama3(device=device)
    
    # 假设元数据文件路径
    metadata_path = './metadata.json'  # 替换为实际路径
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    audio_path = metadata["storage_path"]
    
    # 获取与音频文件同名和路径的JSON文件路径
    json_path = os.path.splitext(audio_path)[0] + '.json'
    
    # 指定威胁文件夹路径
    THREAT_FOLDER = './threat'  # 如果需要，可以更新为实际的威胁文件夹路径

    # 使用Llama3生成解决方案
    generate_solutions(json_path, llama3_instance, THREAT_FOLDER)
