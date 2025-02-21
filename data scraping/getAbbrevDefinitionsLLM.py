import os
import json
from openai import OpenAI
from tqdm import tqdm

#define input and output directories
dataDir = os.path.join("Data Scraping", "Test Outputs")
outputDir = os.path.join("Data Scraping", "Test Outputs")  #temporary test file path

#set input and output JSON file names
fileName = 'generated-data.json'
outputName = 'maths_definitions.json'

#export OPENAI_API_KEY="apikey" to set api key in environment


def loadJSON(dataDir,fileName):
    '''
    Loads JSON file given file directory and filename.
    Inputs:
    dataDir - string, filepath of directory containing JSON.
    fileName - string of filename.
    Outputs:
    data - 
    '''
    filePath = os.path.join(dataDir, fileName)
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
        print("JSON data loaded successfully!")
    except FileNotFoundError:
        print(f"Error: {fileName} was not found in", os.getcwd())
        data = []  #set data to empty list if no file found
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        data = []
    return data

def saveJSON(data,outputDir,outputName):
    '''
    Saves JSON file to output directory.
    Inputs:
    data - data to save to JSON
    outputDir - string of desired output directory
    outputName - string of output JSON file name
    Outputs:
    JSON file of 'data' at outputDir/outputName
    '''

    outputJSON = json.dumps(data, indent=4)
    outputPath = os.path.join(outputDir, outputName)

    try:
        with open(outputPath, 'w') as outputFile:
            outputFile.write(outputJSON)
    except Exception as e:
        print("Error saving results:", e)

def getOpenAIResponse(systemPrompt,
                      userPrompt,
                      model,
                      maxTokens,
                      numResponse,
                      temperature,
                      ):
    '''
    Calls the OpenAI API to generate a response.
    Inputs:
    OPENAI_API_KEY - string for API key set as environment variable.
    systemPrompt - string of pre-prompt high level instructions.
    userPrompt - string for main prompt.
    model - string determining LLM model used.
    maxTokens - integer of maximum tokens in response.
    numResponse - integer number of reponses to generate.
    temerature - float (0-1) temperatyre of response.
    Outputs:
    response - 
    '''
    #setting openai api key from env variable
    OpenAI.api_key = os.getenv("OPENAI_API_KEY")
    
    client = OpenAI() #setting client

    try:
        response = client.chat.completions.create(
            model= model,
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt}
                ],
                max_tokens = maxTokens,
                n=numResponse,
                temperature=temperature
        )
        
        return response
    
    except Exception as e:
        print(f"Error calling OpenAI API.")
        return None

def getAbbrevDefinitionOpenAI(abbrev,context):
    '''
    Finds definition of abbreviation given context, using OpenAI API and 4o-mini model.
    Inputs:
    abbreviation - 
    context - list of contexts of abbreviation
    Outputs - string for definition of abbreviation
    '''

    #prompts
    systemPrompt = f"""
    You are a helpful academic assistant.
    """
    userPrompt = f"""
    Provide an extremely short definition for the abbreviation
    '{abbrev}' as used in the following context {context}. 
    Return only the definition of '{abbrev}' without extra explanation or additional words.
    """

    model = 'gpt-4o-mini'
    maxTokens = 50
    numResponse = 1
    temperature = 0.3

    response = getOpenAIResponse(systemPrompt, userPrompt,model,maxTokens,numResponse,temperature,)

    if response is None:
        print("No response from API")
        return None
    else:
        return response.choices[0].message.content.strip()

#find definition for each abbreviation in json and store result
results = []

data = loadJSON(dataDir,fileName) #load JSON of abbreviations and context

for entry in tqdm(data, desc="Processing entries", unit="entry"):

    abbrev = entry["maths"] #set abbrevation to variable
    contexts = entry["mathsContext"] #set all mentions to context variable

    definitions = []

    for i in range(len(abbrev)):
        definitions.append(getAbbrevDefinitionOpenAI(abbrev[i], contexts[i]))

    results.append({
        "name": entry["name"], 
        "mentions": entry["mentions"], 
        "atlusUrl": entry["atlusUrl"], 
        "paper": entry["paper"], 
        "paperName": entry["paperName"],
        "maths": abbrev, 
        "mathsDefinitions": definitions,
    })

    saveJSON(results,outputDir,outputName)