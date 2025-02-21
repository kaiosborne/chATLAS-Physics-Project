import os
import json
from openai import OpenAI
from tqdm import tqdm

#define input and output directories and input file path
dataDir = os.path.join("Data Scraping", "Test Paper Data")
outputDir = os.path.join("Data Scraping", "Test Outputs")  #temporary test file path
fileName = 'generated-data-maths.json'
filePath = os.path.join(dataDir, fileName)
outputName = 'abbreviation_definitions.json'

#export OPENAI_API_KEY="THEKEY"

client = OpenAI()

#loading json file
try:
    with open(filePath, 'r') as file:
        data = json.load(file)
    print("JSON data loaded successfully!")
except FileNotFoundError:
    print("Error: {fileName} was not found in", os.getcwd())
    data = []  #set data to empty list if no file found
except json.JSONDecodeError as e:
    print("Error decoding JSON:", e)
    data = []

def get_definition_from_openai(abbrev, sentence):
    """
    Calls the OpenAI API to generate a definition for an abbreviation within a context sentence.
    """
    #setting openai from env variable
    api_key = os.getenv("OPENAI_API_KEY")
    OpenAI.api_key = api_key
    
    #prompts
    systemPrompt = f"""
    You are a helpful assistant that is operating 
    in a technical high energy physics context.
    """
    userPrompt = f"""
    Provide an extremely short definition (just one phrase) for the abbreviation
    '{abbrev}' as used in the following contexts: {sentence}. 
    Return only the definition without extra explanation, the returned response 
    should only refer to the abbreviation '{abbrev}'. You should not answer if you 
    are unable to determine a definition with certainty.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt}
                ],
                max_tokens=50,
                n=1,
                temperature=0.5
        )
        
        # Extract the generated text using attribute access
        definition = response.choices[0].message.content.strip()
        return definition
    
    except Exception as e:
        print(f"Error calling OpenAI API for {abbrev}: {e}")
        return None

#find definition for each abbreviation in json and store result
results = []

for entry in tqdm(data, desc="Processing entries", unit="entry"):

    abbrev = entry["name"] #set abbrevation to variable
    context = entry["mentions"] #set all mentions to context variable

    definitions = [] #init list

    definition = get_definition_from_openai(abbrev, context)
    if definition:
        definitions.append(definition)
    
    #collect all definitions for abbrevation
    results.append({
        "abbreviation": abbrev,
        "definitions": definitions
    })


#save results 
output_json = json.dumps(results, indent=4)
output_path = os.path.join(outputDir, outputName)

try:
    with open(output_path, 'w') as output_file:
        output_file.write(output_json)
    print("Results saved to", output_path)
except Exception as e:
    print("Error saving results:", e)