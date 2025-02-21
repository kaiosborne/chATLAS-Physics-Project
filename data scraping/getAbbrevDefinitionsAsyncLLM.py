import os
import json
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio
from pydantic import BaseModel

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")
fileName = 'generated-data.json'
outputName = 'maths_definitions.json'

class mathsDef(BaseModel):
    maths: str
    definition: str

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

CACHE = {}  # To store already processed abbreviations

def loadJSON(dataDir, fileName):
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
            print('JSON file loaded successfully!')
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
    Sends batch requests to OpenAI API with structured JSON output.
    '''
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    
    systemPrompt = "You are a helpful academic assistant. Provide structured output in JSON format."
    
    userPrompt = "\n".join([
        f"""Provide an extremely short definition for '{abbrev}' in this context: {context}. 
        Return only the definition without extra explaination as a JSON with keys 'abbreviation' and 'definition'."""
        for abbrev, context in zip(abbrev_list, context_list)
    ])

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ],
        "max_tokens": 50,
        "temperature": 0.3,
        "n": 1
    }

    while True:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                saveJSON(result, outputDir, outputName)
                print(result)
                try:
                    # Parse JSON response from OpenAI
                    structured_results = json.loads(result["choices"][0]["message"]["content"])
                    return structured_results  # Returns list of JSON objects
                except json.JSONDecodeError:
                    print("Error parsing JSON response. Retrying...")
                    await asyncio.sleep(1)
            elif response.status == 429:  # Handle rate limit errors
                retry_after = int(response.headers.get("Retry-After", 1))
                await asyncio.sleep(retry_after)
            else:
                print(f"API Error: {await response.text()}")
                return [{"abbreviation": abbrev, "definition": None} for abbrev in abbrev_list]

async def process_entry(entry, session, progress_bar):
    '''
    Processes a single entry asynchronously and updates progress bar.
    '''
    abbrev_list = entry["maths"]
    context_list = entry["mathsContext"]

    uncached_abbrevs = []
    uncached_contexts = []
    cached_results = []

    for abbrev, context in zip(abbrev_list, context_list):
        if (abbrev, context) in CACHE:
            cached_results.append(CACHE[(abbrev, context)])
        else:
            uncached_abbrevs.append(abbrev)
            uncached_contexts.append(context)

    if uncached_abbrevs:
        fetched_results = await getOpenAIResponse(uncached_abbrevs, uncached_contexts, session)
        for result in fetched_results:
            CACHE[(result["abbreviation"], context)] = result["definition"]
        cached_results.extend([res["definition"] for res in fetched_results])

    progress_bar.update(1)  # Update progress bar

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
    Main function to handle all entries in parallel with a progress bar.
    '''
    data = loadJSON(dataDir, fileName)
    results = []

    async with aiohttp.ClientSession() as session:
        with tqdm_asyncio(total=len(data), desc="Processing Entries", unit="entry") as progress_bar:
            tasks = [process_entry(entry, session, progress_bar) for entry in data]
            results = await asyncio.gather(*tasks)

# Run async event loop
asyncio.run(main())