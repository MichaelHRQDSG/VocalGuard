import torch
import json
import os
from transformers import BertTokenizer, BertForSequenceClassification

def predict_single_text(text, model_path='./saved_cn_bert_model/', label_map=None):
    # Load the saved model and tokenizer
    tokenizer = BertTokenizer.from_pretrained(model_path, local_files_only=True)
    model = BertForSequenceClassification.from_pretrained(model_path, local_files_only=True)

    # Move the model to CUDA if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # Preprocess input text
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)

    # Model inference
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_label_id = torch.argmax(logits, axis=1).item()
        print(predicted_label_id)
        
    predicted_label_text = label_map[str(predicted_label_id)]    
    print(predicted_label_text)
    # Convert label ID to label text if a mapping is provided
    return predicted_label_text

def process_metadata(metadata_path, model_path='./saved_cn_bert_model'):
    label_map_path="./saved_cn_bert_model/label_map.json"
    with open(label_map_path, 'r', encoding='utf-8') as f:
        label_map = json.load(f)
    

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Get the transcription field
    transcription = metadata.get("transcription", "")
    print(transcription)
    if not transcription:
        print(f"No transcription found in {metadata_path}. Skipping.")
        return

    # Perform text classification inference
    predicted_label_text = predict_single_text(transcription, model_path=model_path, label_map=label_map)
    
    # Update the metadata with the classification result
    if "detection_context" not in metadata:
        metadata["detection_context"] = {"result": {}}
    if "result" not in metadata["detection_context"]:
        metadata["detection_context"]["result"] = {}

    # Add the predicted label text as the classification result
    metadata["detection_context"]["result"]["classification_completed"] = True
    metadata["detection_context"]["result"]["classification_result"] = predicted_label_text

    # Write the updated metadata back to the JSON file
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"Metadata updated with classification result for {metadata_path}")

if __name__ == "__main__":
    # Assume the metadata file path
    metadata_path = './metadata.json'  # Replace with the actual path
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    audio_path = metadata["storage_path"]
    print(audio_path)
    
    # Get the JSON file path with the same name and path as the audio file
    json_path = os.path.splitext(audio_path)[0] + '.json'
    process_metadata(json_path)