import os
from transformers import pipeline

# Initialize a local text generation pipeline with a chat-capable model.
# You can change 'microsoft/DialoGPT-medium' to any other compatible local model.
generator = pipeline('text-generation', model='microsoft/DialoGPT-medium')

def getLocalResponse(systemPrompt, userPrompt, maxTokens, numResponse, temperature):
    """
    Generates a response using a local language model.

    Args:
        systemPrompt (str): The system-level prompt.
        userPrompt (str): The user prompt.
        maxTokens (int): Maximum tokens for the response.
        numResponse (int): Number of responses to generate.
        temperature (float): Sampling temperature.

    Returns:
        str: The generated response content.
    """
    # Combine system and user prompts into a conversation context.
    prompt = f"System: {systemPrompt}\nUser: {userPrompt}\nAssistant:"
    
    # Generate responses using the local model.
    responses = generator(prompt,
                          max_length=maxTokens,
                          num_return_sequences=numResponse,
                          temperature=temperature)
    
    # Extract and clean up the response from the first generated output.
    generated_text = responses[0]['generated_text']
    generated_response = generated_text[len(prompt):].strip()
    return generated_response

def getSearchSuggestion(user_search):
    """
    Generates a clarifying question for the user's search query using a local language model.

    Args:
        user_search (str): The user's original search query.

    Returns:
        str: The clarifying question.
    """
    systemPrompt = "You are a helpful academic assistant, in a high energy physics context."
    userPrompt = (
        f"A user has submitted the following search query: '{user_search}'. "
        "To help refine this search for better results, please provide one SHORT suggestion to alter the user search. "
        "Your question should guide the user to indicate specific areas and write variables in full for clarity. "
        "Frame the question as a suggestion to alter the search prompt."
    )
    return getLocalResponse(systemPrompt, userPrompt, maxTokens=100, numResponse=1, temperature=0.3)

def generateQueries(user_search, num_queries):
    """
    Generates queries for the user's search query using a local language model.

    Args:
        user_search (str): The user's original search query.
        num_queries (int): Number of additional queries to return.

    Returns:
        str: The additional queries.
    """
    systemPrompt = (
        "You are a helpful academic assistant, in a high energy physics context. "
        "Your role is to generate multiple search queries based on a single input query."
    )
    userPrompt = (
        f"A user has submitted the following search query: '{user_search}'. "
        f"Generate {num_queries} search queries, one on each line, related to the input query: '{user_search}'"
    )
    return getLocalResponse(systemPrompt, userPrompt, maxTokens=150, numResponse=1, temperature=0.1)

if __name__ == "__main__":
    # Get the user's search query
    user_search = input("Enter your search query: ")
    
    # Generate a clarifying question for the search query
    clarifying_question = getSearchSuggestion(user_search)
    print("\nClarifying question:", clarifying_question)
    
    # Generate multiple related search queries
    generated_queries = generateQueries(user_search, num_queries=3)
    print("\nGenerated queries:", generated_queries)