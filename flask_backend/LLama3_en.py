import torch
import json
import os
import re
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

    def generate(self, messages):
        outputs = self.pipeline(messages, max_new_tokens=512, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
        return outputs[0]["generated_text"]

def detect_amount_and_urgency(text):
    # Regular expressions for matching amounts and urgency
    amount_pattern = r'Amount description:\s*([^\n]*)'
    urgency_pattern = r'Time urgency:\s*([^\n]*)'

    amounts = re.findall(amount_pattern, text)
    urgency_phrases = re.findall(urgency_pattern, text)

    # Return None if no matches are found
    return amounts[0] if amounts else "None", urgency_phrases[0] if urgency_phrases else "None"

def transcribe_from_metadata(metadata_path):
    # Read metadata.json file to get audio path and perform transcription.
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    audio_path = metadata.get("storage_path")
    if not os.path.exists(audio_path):
        return None
    
    json_path = os.path.splitext(audio_path)[0] + '.json'
    with open(json_path, 'r') as f:
        metadata2 = json.load(f)

    return metadata2.get("transcription", "")

def process_transcription_and_detect(metadata_path, llama3_instance):
    transcription = transcribe_from_metadata(metadata_path)
    if not transcription:
        return "No transcription available."

    prompt = f"""
    Please analyze the following transcription to extract only clearly quantified financial amounts and time urgencies. If there is no explicit mention of such values, output "None" for each field. Strictly adhere to the format and do not provide any unrelated analysis or commentary. Only provide Amount description and Time urgency in the response, and nothing else.
    {transcription}
    Example Response Format:
    - Amount description: 1000 dollars
    - Time urgency: 24 hours 
    if there is no such data:
    - Amount description: None
    - Time urgency: None
    
    Provide your response:
    """
    generated_text = llama3_instance.generate(prompt)
    response_start = generated_text.split("Provide your response:")[-1].strip()
    print(response_start)
    amounts, urgency_phrases = detect_amount_and_urgency(response_start)

    with open(metadata_path, 'r', encoding='utf-8', errors='replace') as f:
        metadata1 = json.load(f)
    audio_path = metadata1["storage_path"]
    json_path = os.path.splitext(audio_path)[0] + '.json'

    with open(json_path, 'r', encoding='utf-8', errors='replace') as f:
        metadata = json.load(f)

    # Update metadata with detection results
    metadata.setdefault("detection_context", {"result": {}})
    metadata["detection_context"]["result"].update({
        "money_amount": amounts,
        "time": urgency_phrases
    })

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    return f"Metadata updated with detected amount: {amounts} and time urgency: {urgency_phrases} for {metadata_path}"

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    llama3_instance = Llama3(device=device)
    
    metadata_path = "./metadata.json"  # Change to your actual metadata.json path
    result = process_transcription_and_detect(metadata_path, llama3_instance)
    print(result)
