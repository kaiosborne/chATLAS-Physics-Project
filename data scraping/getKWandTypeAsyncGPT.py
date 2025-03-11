import openai
import re
import json
import os
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio  # async version of tqdm

# Set Input and output files (relative path)
#input_file = os.path.join("Data Scraping", "Test Outputs", "generated-data2.json")
#output_file = os.path.join("Data Scraping", "Test Outputs", "generated-data3.json")
# Set Input and output files (absolute path)
#input_file = r"C:\Users\maths_definitions.json"
#output_file = r"C:\Users\extracted_keywords.json"

# Linux/macOS  : enter "export OPENAI_API_KEY="yourkey" " in bash
# Windows(CMD): enter "set OPENAI_API_KEY=yourkey " in cmd
# WIndows(PS) : enter "$env:OPENAI_API_KEY="your-api-key-here" " in powershell

# Preprocess the texts, remove LaTeX commands
def preprocess_text(text):
    # Remove LaTeX commands 
    text = re.sub(r'\\[^ ]+', '', text)
    # Remove extra spaces and newline breaks
    text = ' '.join(text.split())
    return text

categories = [
    "Event Display", "Kinematic Distribution Plot", "Data vs. Monte Carlo Comparison Plot",
    "Exclusion Limit Plot", "Efficiency Curve", "Detector Schematics and Layouts",
    "Correlation or Scatter Plot", "Residual or Pull Distribution", "Control Region Plot", "others"
]

# Extract keywords asynchronously
async def extract_keywords(session, text):
    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful academic assistant in a high energy physics (ATLAS) context. "
                            f"Return a few domain-specific and technical keywords, and exactly one figure type from these categories: {categories}. "
                            "Format the response as: 'Keywords: kw1, kw2, kw3; Plot type: [category]'. "
                            "Do not return any additional information or explanations."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Extract the most important keywords and one figure type from this text:\n{text}\n"
                            "Format the response as: 'Keywords: kw1, kw2, kw3; Plot type: [category]'. "
                            "Do not add extra words, explanations, or formatting."
                        )
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
        ) as response:
            data = await response.json()
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"keywords": [], "Plot type": ""}

# Process figures concurrently with a progress bar
async def process_figures(input_file, output_file):
    """Process data set and save results."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for figure in data:
            combined_text = " ".join(figure['mentions'])
            cleaned_text = preprocess_text(combined_text)
            task = extract_keywords(session, cleaned_text)
            tasks.append((figure, task))
        
        # Create a list of all keyword extraction tasks
        keyword_tasks = [task for _, task in tasks]
        # Await all tasks with a progress bar
        keywords_results = await tqdm_asyncio.gather(*keyword_tasks, desc="Extracting keywords", total=len(tasks))
        
        # Combine the figures with their corresponding keywords
        for (figure, _), keywords in zip(tasks, keywords_results):
            try:
                if isinstance(keywords, str):
                    # 假设 GPT 直接返回文本格式，如 "Keywords: kw1, kw2, kw3; Plot type: Exclusion Limit Plot"
                    if ";" in keywords:
                        keywords_part, plot_type_part = keywords.split(";")
                        keywords_text = keywords_part.replace("Keywords:", "").strip()
                        plot_type_text = plot_type_part.replace("Plot type:", "").strip()
                    else:
                        keywords_text = ""
                        plot_type_text = ""
                else:
                    keywords_text = ""
                    plot_type_text = ""
            except Exception as e:
                print(f"Failed to parse keywords for figure {figure.get('name', 'Unknown')}: {e}")
                keywords_text = ""
                plot_type_text = ""

            figure["keywords"] = keywords_text
            figure["Plot type"] = plot_type_text
            results.append(figure)
    
    # Save the results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

# Check if the input file exists, exit if not
if not os.path.exists(input_file):
    print(f"Input file not found: {input_file}")
    exit(1)

# Check if the output directory exists, create it if not
output_dir = os.path.dirname(output_file)
if not os.path.exists(output_dir):
    print(f"Output directory not found, trying to create: {output_dir}")
    try:
        os.makedirs(output_dir)
    except OSError as error:
        print(f"Failed to create output directory: {error}")
        exit(1)

# Run the asynchronous processing
asyncio.run(process_figures(input_file, output_file))