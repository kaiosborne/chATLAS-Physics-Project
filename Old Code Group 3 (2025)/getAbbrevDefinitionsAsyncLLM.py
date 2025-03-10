import os
import json
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio
from pydantic import BaseModel

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")
fileName = 'generated-data.json'
outputName = 'maths_definitionsslow.json'

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
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}",}

    # Force OpenAI to return JSON by making the format explicit
    systemPrompt = "\n".join([
        "You are a helpful academic assistant."

    ])

    userPrompt = "\n".join([
        f"""Provide an extremely short definition for the abbreviation
        '{abbrev}' as used in the following context {context}. 
        Return only the definition of '{abbrev}' without extra explanation or additional words."""
        for abbrev, context in zip(abbrev_list, context_list)
    ])

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ],
        "max_tokens": 500,
        "temperature": 0.2,
        "n": 1
    }

    while True:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                try:
                    return [choice['message']['content'].strip() for choice in result["choices"]]
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

    entry["mathsDefinitions"] = entry.pop("mathsContext")
    entry["mathsDefinitions"] = cached_results

    return entry

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