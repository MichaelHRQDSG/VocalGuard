import json
import os
import re
import torch
from transformers import pipeline, LlamaForCausalLM, LlamaTokenizer

class Llama3:
    def __init__(self, device, local_model_path) -> None:
        self.device = device
        self.local_model_path = local_model_path
        self.model = LlamaForCausalLM.from_pretrained(local_model_path, torch_dtype=torch.bfloat16)
        self.tokenizer = LlamaTokenizer.from_pretrained(local_model_path)
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if device == "cuda" else -1,
        )

    def generate(self, prompt):
        outputs = self.pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
        return outputs[0]["generated_text"]

def clean_response(text):
    # Remove excessive whitespace, newlines, and unwanted characters
    cleaned_text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces and newlines into a single space
    return cleaned_text.strip()

def detect_and_categorize_documents(detection_results):
    legal_pattern = re.compile(r'\b(?:Legal|法务部文件)\b')
    tech_pattern = re.compile(r'\b(?:Technical|技术部文件)\b')
    hr_pattern = re.compile(r'\b(?:HR|人事文件)\b')

    legal_docs = []
    tech_docs = []
    hr_docs = []

    for key, value in detection_results.items():
        if legal_pattern.search(str(value)):
            legal_docs.append({key: value})
        if tech_pattern.search(str(value)):
            tech_docs.append({key: value})
        if hr_pattern.search(str(value)):
            hr_docs.append({key: value})

    return legal_docs, tech_docs, hr_docs

def generate_department_solution(docs, department_name, llama3_instance):
    prompt = f"""
    Based on the following detection results for {department_name.replace('_', ' ')}:
    {json.dumps(docs, indent=4)}
    Provide specific and actionable tasks for each department to handle the situation, ensure that every department has a comprehensive and actionable plan tailored to handle the situation effectively. Please only provide the answer, and do not repeat the question or detection results.
    """
    try:
        solution_content = llama3_instance.generate(prompt).strip()
        solution_content = clean_response(solution_content)
        cutoff_point = solution_content.find("Please only provide the answer, and do not repeat the question or detection results.")
        if cutoff_point != -1:
            solution_content = solution_content[cutoff_point + len("Please only provide the answer, and do not repeat the question or detection results."):].strip()
    except Exception as e:
        print(f"Error generating solution for {department_name} with Llama3: {str(e)}")
        solution_content = {
            "error": f"Failed to generate solution for {department_name} using Llama3.",
            "details": str(e)
        }
    return solution_content

def generate_solutions(json_file_path, llama3_instance, threat_folder):
    with open(json_file_path, 'r') as json_file:
        detection_results = json.load(json_file)

    legal_docs, tech_docs, hr_docs = detect_and_categorize_documents(detection_results)

    solutions = {
        "Legal_Department_Solution": generate_department_solution(legal_docs, "Legal Department", llama3_instance),
        "Technical_Department_Solution": generate_department_solution(tech_docs, "Technical Department", llama3_instance),
        "HR_Department_Solution": generate_department_solution(hr_docs, "HR Department", llama3_instance)
    }

    os.makedirs(threat_folder, exist_ok=True)

    combined_content = {
        "original_json": detection_results,
        "department_solutions": solutions
    }

    solution_file_path = os.path.join(threat_folder, os.path.basename(os.path.splitext(json_file_path)[0]) + '_solution.json')
    with open(solution_file_path, 'w') as solution_file:
        json.dump(combined_content, solution_file, indent=4)

    print(f"Solutions generated and saved to {solution_file_path}.")
    return solution_file_path

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    local_model_path = "./local_llama_model"  # 本地模型路径

    llama3_instance = Llama3(device=device, local_model_path=local_model_path)

    metadata_path = './metadata.json'  # 替换为实际路径
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    audio_path = metadata["storage_path"]
    json_path = os.path.splitext(audio_path)[0] + '.json'
    THREAT_FOLDER = './threat'

    generate_solutions(json_path, llama3_instance, THREAT_FOLDER)