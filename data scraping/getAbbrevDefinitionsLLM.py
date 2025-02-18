import os
import json
from openai import OpenAI
from tqdm import tqdm

#define input and output directories
dataDir = os.path.join("Data Scraping", "Test Paper Data")
outputDir = os.path.join("Data Scraping", "Test Outputs")  #temporary test file path

#set input and output JSON file names
fileName = 'generated-data-maths.json'
outputName = 'maths_definitions.json'

#export OPENAI_API_KEY="apikey"


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
        print("Results saved to", outputPath)
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

def getAbbrevDefinitionLLM(abbrev,context):
    '''
    Finds definition of abbreviation given context, using OpenAI API and 4o-mini model.
    Inputs:
    abbreviation - 
    context - list of contexts of abbreviation
    Outputs - string for definition of abbreviation
    '''

    #prompts
    systemPrompt = f"""
    You are a helpful academic assistant that is operating 
    in a technical high energy physics context.
    """
    userPrompt = f"""
    Provide an extremely short definition (just one phrase) for the abbreviation
    '{abbrev}' as used in the following contexts: {context}. 
    Return only the definition without extra explanation, the returned response 
    should only refer to the abbreviation '{abbrev}'. You should not answer if you 
    are unable to determine a definition with certainty.
    """

    model = 'gpt-4o-mini'
    maxTokens = 50
    numResponse = 1
    temperature = 0.5

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

    abbrev = entry["name"] #set abbrevation to variable
    context = entry["mentions"] #set all mentions to context variable

    results.append({
        "abbreviation": abbrev,
        "definition": getAbbrevDefinitionLLM(abbrev, context)
    })

saveJSON(results,outputDir,outputName)