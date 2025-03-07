import os
import requests

def getOpenAIResponse(systemPrompt, userPrompt, model, maxTokens, numResponse, temperature):
    """
    Sends a request to the OpenAI Chat API and returns the generated response.
    
    Args:
        systemPrompt (str): The system-level prompt.
        userPrompt (str): The user prompt.
        model (str): The model identifier (e.g., 'gpt-4o-mini').
        maxTokens (int): Maximum tokens for the response.
        numResponse (int): Number of responses to generate.
        temperature (float): Sampling temperature.
    
    Returns:
        str or None: The generated response content, or None if there was an error.
    """
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
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        resp_json = response.json()
        return resp_json["choices"][0]["message"]["content"].strip()
    else:
        print(f"Error: {response.status_code}")
        return None

def getSearchSuggestion(user_search):
    """
    Generates a clarifying question for the user's search query using the OpenAI Chat API.
    
    Args:
        user_search (str): The user's original search query.
    
    Returns:
        str or None: The clarifying question, or None if an error occurred.
    """
    systemPrompt = "You are a helpful academic assistant, in a high energy physics context."
    userPrompt = (
        f"""A user has submitted the following search query: '{user_search}'.
        To help refine this search for better results, please provide one SHORT suggestion to alter the user search. 
        Your question should guide the user to indicate specific areas and write variables in full for clarity.
        Frame the question as a suggestion to alter the search prompt.
        """
    )
    return getOpenAIResponse(systemPrompt, userPrompt, model='gpt-4o-mini', maxTokens=150, numResponse=1, temperature=0.3)

def generateQueries(user_search,num_queries):
    """
    Generates quries for the user's search query using the OpenAI Chat API.
    
    Args:
        user_search (str): The user's original search query.
        num_queries (int): Number of additional queries to return.
    Returns:
        string, list, or None: The additional queries, or None if an error occurred.
    """
    systemPrompt = (
        """
        You are a helpful academic assistant, in a high energy physics context.
        Your role is to generate multiple search queries based on a single input query.
        """
    )
    userPrompt = (
        f"""
        A user has submitted the following search query: '{user_search}'. "
        Generate {num_queries} search queries, one on each line, related to the input query: '{user_search}'
        """
    )
    return getOpenAIResponse(systemPrompt, userPrompt, model='gpt-4o-mini', maxTokens=50, numResponse=1, temperature=0.1)

#testing
if __name__ == "__main__":
    # Get the user's search query
    user_search = input("Enter your search query: ")
    
    # Generate a clarifying question for the search query
    clarifying_question = getSearchSuggestion(user_search)
    print("\nClarifying question:", clarifying_question)
    
    # Generate multiple related search queries using GPT-3.5-turbo
    generated_queries = generateQueries(user_search, num_queries=3)
    print("\nGenerated queries:", generated_queries)
    