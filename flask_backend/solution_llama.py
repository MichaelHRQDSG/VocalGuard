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
        outputs = self.pipeline(prompt, max_new_tokens=1024, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
        return outputs[0]["generated_text"]

def clean_response(text):
    # Remove excessive whitespace, newlines, and unwanted characters
    cleaned_text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces and newlines into a single space
    return cleaned_text.strip()

def generate_solution_with_llama3(json_file_path, llama3_instance, threat_folder):
    # Load the detection results from the JSON file
    with open(json_file_path, 'r') as json_file:
        detection_results = json.load(json_file)

    # Construct a prompt for Llama3 using detection results
    prompt = f"""
    Based on the following detection results:
    {json.dumps(detection_results, indent=4)}
    
    Generate a response plan with the following structure:
    Task: 
    Responsible Departments: 
      - Legal Department Task:
      - Business Department Task:
      - Algorithm Department Task:
      - Customer Service Task:
    
    Provide specific and actionable tasks for each department to handle the situation.
    """

    # Generate solution using Llama3
    try:
        solution_content = llama3_instance.generate(prompt).strip()
        solution_content = clean_response(solution_content)  # Clean up the response
    except Exception as e:
        print(f"Error generating solution with Llama3: {str(e)}")
        solution_content = {
            "error": "Failed to generate solution using Llama3.",
            "details": str(e)
        }

    # Ensure the threat folder exists
    if not os.path.exists(threat_folder):
        os.makedirs(threat_folder)

    # Save the generated solution to a new JSON file in the threat folder
    solution_file_path = os.path.join(threat_folder, os.path.basename(os.path.splitext(json_file_path)[0]) + '_solution.json')
    with open(solution_file_path, 'w') as solution_file:
        if isinstance(solution_content, str):
            try:
                # Convert string response to dictionary if possible
                solution_content = json.loads(solution_content)
            except json.JSONDecodeError:
                # If it fails, save as plain text
                solution_content = {"llama3_response": solution_content}
        json.dump(solution_content, solution_file, indent=4)

    print(f"Solution generated and saved to {solution_file_path}.")
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
    THREAT_FOLDER = './threat'  # Update this to your actual threat folder path if necessary

    # Generate solution using Llama3
    generate_solution_with_llama3(json_path, llama3_instance, THREAT_FOLDER)
