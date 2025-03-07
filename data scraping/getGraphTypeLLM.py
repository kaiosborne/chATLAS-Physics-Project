import json
import torch
from PIL import Image
import requests
from transformers import CLIPProcessor, CLIPModel
import concurrent.futures

# need to pip install torch transformers pillow requests

# Load the CLIP model and processor from Hugging Face.
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Define the ATLAS figure categories.
categories = [
    "Event Display",
    "Kinematic Distribution Plot",
    "Data vs. Monte Carlo Comparison Plot",
    "Exclusion Limit Plot",
    "Efficiency Curve",
    "Detector Schematics and Layouts",
    "Correlation or Scatter Plot",
    "Residual or Pull Distribution",
    "Control Region Plot"
]

# Create text prompts for each category.
prompts = [f"A high quality {cat} in an ATLAS publication." for cat in categories]

def download_image(url):
    """
    Download an image from the provided URL and convert it to RGB.
    Returns the PIL Image object if successful, otherwise None.
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        return Image.open(response.raw).convert("RGB")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

def process_batch(objects, model, processor, prompts, categories):
    """
    For a batch of JSON objects, download images concurrently from the 'imageUrls' field,
    use CLIP in batch mode to classify each image into one of the predefined categories,
    and update each object with a new key 'FigureType'.
    """
    image_urls = [obj.get("imageUrls", "") for obj in objects]
    
    # Download images concurrently while preserving order.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        images = list(executor.map(download_image, image_urls))
    
    # Prepare lists for images that successfully downloaded.
    images_to_classify = []
    valid_indices = []
    for idx, img in enumerate(images):
        if img is not None:
            images_to_classify.append(img)
            valid_indices.append(idx)
    
    # If we have any images, classify them in batch.
    if images_to_classify:
        inputs = processor(text=prompts, images=images_to_classify, return_tensors="pt", padding=True)
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image  # shape: (num_valid_images, len(prompts))
        probs = logits_per_image.softmax(dim=1)
        best_indices = probs.argmax(dim=1).tolist()
    else:
        best_indices = []
    
    # Create a result list for the entire batch.
    batch_results = []
    valid_idx = 0
    for idx in range(len(objects)):
        if images[idx] is None:
            batch_results.append("Unknown")
        else:
            category = categories[best_indices[valid_idx]]
            batch_results.append(category)
            valid_idx += 1
    
    # Update each object in the batch with the classification result.
    for obj, figure_type in zip(objects, batch_results):
        obj["FigureType"] = figure_type

def process_json_in_batches(input_file, output_file, batch_size=16):
    """
    Process the JSON file in batches: for each batch, download and classify the images
    using CLIP, add a new key 'FigureType' to each object, and write the updated JSON to the output file.
    """
    # Load the JSON data.
    with open(input_file, "r", encoding="utf-8") as infile:
        data = json.load(infile)
    
    total = len(data)
    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]
        process_batch(batch, clip_model, clip_processor, prompts, categories)
        print(f"Processed batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
    
    # Write the updated data to the output file.
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)
    
    print(f"Transformation completed. Check the file: {output_file}")

if __name__ == "__main__":
    process_json_in_batches("DB.json", "DB_new.json", batch_size=16)
