import os
import json
import asyncio
import aiohttp
from tqdm import tqdm

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")
fileName = 'generated-data.json'
outputName = 'maths_definitions.json'

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

CACHE = {}  # To store already processed abbreviations

def loadJSON(dataDir, fileName):
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("Error:", e)
        return []

def saveJSON(data, outputDir, outputName):
    outputPath = os.path.join(outputDir, outputName)
    with open(outputPath, 'w') as outputFile:
        json.dump(data, outputFile, indent=4)

async def getOpenAIResponse(abbrev_list, context_list, session):
    '''
    Sends batch requests to OpenAI API.
    '''
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    systemPrompt = "You are a helpful academic assistant."
    userPrompt = "\n".join([
        f"Provide an extremely short definition for '{abbrev}' in this context: {context}."
        for abbrev, context in zip(abbrev_list, context_list)
    ])
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ],
        "max_tokens": 50,
        "temperature": 0.3,
        "n": 1
    }

    async with session.post(API_URL, headers=headers, json=payload) as response:
        if response.status == 200:
            result = await response.json()
            return [choice['message']['content'].strip() for choice in result["choices"]]
        else:
            print(f"API Error: {await response.text()}")
            return [None] * len(abbrev_list)

async def process_entry(entry, session):
    '''
    Processes a single entry asynchronously.
    '''
    abbrev_list = entry["maths"]
    context_list = entry["mathsContext"]

    # Check cache to avoid redundant API calls
    uncached_abbrevs = []
    uncached_contexts = []
    cached_results = []

    for abbrev, context in zip(abbrev_list, context_list):
        if (abbrev, context) in CACHE:
            cached_results.append(CACHE[(abbrev, context)])
        else:
            uncached_abbrevs.append(abbrev)
            uncached_contexts.append(context)

    # Fetch only uncached results
    if uncached_abbrevs:
        fetched_results = await getOpenAIResponse(uncached_abbrevs, uncached_contexts, session)
        for abbrev, context, result in zip(uncached_abbrevs, uncached_contexts, fetched_results):
            CACHE[(abbrev, context)] = result
        cached_results.extend(fetched_results)

    return {
        "name": entry["name"],
        "mentions": entry["mentions"],
        "atlusUrl": entry["atlusUrl"],
        "paper": entry["paper"],
        "paperName": entry["paperName"],
        "maths": abbrev_list,
        "mathsDefinitions": cached_results
    }

async def main():
    '''
    Main function to handle all entries in parallel.
    '''
    data = loadJSON(dataDir, fileName)
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = [process_entry(entry, session) for entry in data]
        results = await asyncio.gather(*tasks)

    saveJSON(results, outputDir, outputName)

# Run async event loop
asyncio.run(main())