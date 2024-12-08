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
        outputs = self.pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
        print(outputs)
        return outputs[0]["generated_text"]

def clean_response(text):
    # Remove excessive whitespace, newlines, and unwanted characters
    cleaned_text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces and newlines into a single space
    return cleaned_text.strip()

def generate_department_solution(text, department_name, llama3_instance):
    # Construct a prompt for the department
    prompt = f"""
    Now there is a potential fake audio detection result: {text}:
    Provide specific and actionable solution for {department_name} to handle the situation. Please only provide the answer, and do not repeat the question or detection results.
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
    # Load the detection results from the JSON file
    with open(json_file_path, 'r') as json_file:
        detection_results = json.load(json_file)

    # Generate solutions for each department
    solutions = {
        "Legal_Department_Solution": generate_department_solution(detection_results, "Legal Department", llama3_instance),
        "Technical_Department_Solution": generate_department_solution(detection_results, "Technical Department", llama3_instance),
        "HR_Department_Solution": generate_department_solution(detection_results, "HR Department", llama3_instance)
    }

    # Ensure the threat folder exists
    os.makedirs(threat_folder, exist_ok=True)

    # Prepare content to save in the JSON file
    combined_content = {
        "original_json": detection_results,
        "department_solutions": solutions
    }

    # Save the combined content to a new JSON file in the threat folder
    solution_file_path = os.path.join(threat_folder, os.path.basename(os.path.splitext(json_file_path)[0]) + '_solution.json')
    with open(solution_file_path, 'w') as solution_file:
        json.dump(combined_content, solution_file, indent=4)

    print(f"Solutions generated and saved to {solution_file_path}.")
    return solution_file_path

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    llama3_instance = Llama3(device=device)
    
    # Assume the metadata file path
    metadata_path = './metadata.json'  # Replace with the actual path
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    audio_path = metadata["storage_path"]
    
    # Get the JSON file path with the same name and path as the audio file
    json_path = os.path.splitext(audio_path)[0] + '.json'
    
    # Specify the threat folder path
    THREAT_FOLDER = './threat'  
    # Update this to your actual threat folder path if necessary

    # Generate solutions using Llama3
    generate_solutions(json_path, llama3_instance, THREAT_FOLDER)