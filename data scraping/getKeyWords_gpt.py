import openai
import re
import json
import os
import asyncio
import aiohttp

# Openai package required

openai.api_key = 'api' # Enter openai api key here

# Preprocess the texts, remove latex commands
def preprocess_text(text):
    # Remove Latex commands 
    text = re.sub(r'\\[^ ]+', '', text)
    # Remove extra spaces and newline breaks
    text = ' '.join(text.split())
    return text

# Extract keywords asynchronously
async def extract_keywords(session, text):
    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai.api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are an academic assistant, please help me to extract keywords for each following mention"},
                    {"role": "user", "content": f"Please extract the 5 most important keywords from the following text. The keywords should reflect the core content of the Plot or Table:\n{text}"}
                ],
                "max_tokens": 50,
                "temperature": 0.3
            }
        ) as response:
            data = await response.json()
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Process concurrently
async def process_figures(input_file, output_file):
    """process data set and save results"""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
    
        for figure in data:
            print(f"Processing {figure['name']}...")
            print(f"from paper:{figure['paperName']}")
            combined_text = " ".join(figure['mentions'])
            cleaned_text = preprocess_text(combined_text)
            task = extract_keywords(session,cleaned_text)
            tasks.append((figure,task))
            
        for figure, task in tasks:
            keywords = await task
            print(f"keywords:{keywords}")

            
            result = {
                "name": figure['name'],
                "keywords": keywords,
                "paperName": figure['paperName'],
                "atlusUrl": figure['atlusUrl'],
                "originalMentions": figure['mentions']
            }
            results.append(result)
    
    # Save the results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


# Set Input and output files
# NEED TO CHANGE
input_file = '/Users/Jiayi/Desktop/project_code/processed_papers.json'
output_file = '/Users/Jiayi/Desktop/project_code/extracted_keywords.json'

# Check if the input file exists, exit if not
if not os.path.exists(input_file):
    print(f"Input file not found: {input_file}")
    exit(1)

# Check if the output directory exists, create it if not
output_dir = os.path.dirname(output_file)  # Extract the directory part from the output file path
if not os.path.exists(output_dir):
    print(f"Output directory not found, trying to create: {output_dir}")
    try:
        os.makedirs(output_dir)
    except OSError as error:
        print(f"Failed to create output directory: {error}")
        exit(1)

# Runt he asynchronous processing
asyncio.run(
process_figures(
    input_file,output_file
)
)
