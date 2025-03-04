from transformers import T5ForConditionalGeneration, T5Tokenizer
from tqdm import tqdm

# Load a pre-trained T5 model for question generation
# (This model is fine-tuned for generating questions; you can choose another model if desired)
model_name = "valhalla/t5-small-qa-qg-hl"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def generate_clarifying_question(user_search):
    """
    Generates a clarifying question based on the user's search query.
    """
    # Construct a prompt to instruct the model to generate a clarifying question
    prompt = f"generate clarifying question: {user_search}"
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    # Optionally display a progress bar for the generation step
    for _ in tqdm(range(1), desc="Generating clarifying question"):
        output_ids = model.generate(input_ids, max_length=50, num_beams=5, early_stopping=True)
    
    question = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return question

if __name__ == "__main__":
    user_search = input("Enter your search query: ")
    clarifying_question = generate_clarifying_question(user_search)
    print("\nClarifying question:", clarifying_question)