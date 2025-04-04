import os
import json
import asyncio
import aiohttp
from tqdm.asyncio import tqdm_asyncio
import backoff

dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")
fileName = 'generated-data.json'
outputName = 'generated-data2.json'

#export OPENAI_API_KEY="yourkey" in terminal

class RateLimitError(Exception):
    pass

def loadJSON(dataDir, fileName):
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
    except Exception as e:
        print("Error loading JSON:", e)
        data = []
    return data

def saveJSON(data, outputDir, outputName):
    outputPath = os.path.join(outputDir, outputName)
    try:
        with open(outputPath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving JSON:", e)

@backoff.on_exception(backoff.expo, RateLimitError, max_tries=10, jitter=backoff.full_jitter)
async def getOpenAIResponse(session, systemPrompt, userPrompt, model, maxTokens, numResponse, temperature):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": userPrompt}
        ],
        "max_tokens": maxTokens,
        "n": numResponse,
        "temperature": temperature
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    url = "https://api.openai.com/v1/chat/completions"

    async with session.post(url, json=payload, headers=headers) as response:
        if response.status == 200:
            resp_json = await response.json()
            return resp_json["choices"][0]["message"]["content"].strip()
        elif response.status == 429:
            response_body = await response.text()
            raise RateLimitError(f"Rate limit exceeded: {response_body}")
        else:
            print(f"Error: {response.status}")
            return None
        
async def getAbbrevDefinitionOpenAI(session, abbrev, context):

    systemPrompt = "You are a helpful academic assistant, in a high energy physics (ATLAS) context, return answers using domain specific and technical keywords."

    userPrompt = f"""Provide an EXTREMELY SHORT definition for the abbreviation
                '{abbrev}' as used in the following context: '{context}'. 
                Return ONLY the definition of '{abbrev}' without extra explanation or additional words."""
    return await getOpenAIResponse(session, systemPrompt, userPrompt,
                                     model='gpt-4o-mini', maxTokens=50,
                                     numResponse=1, temperature=0.1)

async def processEntry(session, entry):
    abbrev = entry["maths"]
    contexts = entry["mathsContext"]
    definitions = []
    tasks = []
    abbrevs = []
    for a, ctx in zip(abbrev, contexts):
        tasks.append(getAbbrevDefinitionOpenAI(session, a, ctx))
        abbrevs.append(a)
    # Gather results concurrently
    definitions = await asyncio.gather(*tasks)

    del entry["mathsContext"]
    entry["mathsDefinitions"] = definitions

    return entry

async def main():
    data = loadJSON(dataDir, fileName)
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [processEntry(session, entry) for entry in data]
        # Using tqdm for asynchronous progress monitoring
        for coro in tqdm_asyncio.as_completed(tasks, desc="Processing entries", total=len(tasks)):
            result = await coro
            results.append(result)
        saveJSON(results, outputDir, outputName)

if __name__ == '__main__':
    asyncio.run(main())