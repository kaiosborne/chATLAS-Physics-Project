import openai
import re

openai.api_key = 'apikey'

# Preprocess the texts, remove latex commands
def preprocess_text(text):
    # Remove Latex commands 
    text = re.sub(r'\\[^ ]+', '', text)
    # Remove extra spaces and newline breaks
    text = ' '.join(text.split())
    return text

# Extract keywords
def extract_keywords(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a academic assistant, please help me to extract keywords for each following mention "},
                {"role": "user", "content": f"Please extract the 5 most important keywords from the following text. The keywords should reflect the core content of the Plot or Table：\n{text}"}
            ],
            max_tokens=50,
            temperature=0.3  
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Test data
data = [
    {
        "name": "Figure 1",
        "mentions": [
            "Expected yields from simulated signal and background processes, normalized to estimates from data where appropriate, are shown in Fig. 1 as a function of jet multiplicity for events satisfying the complete dilepton event selection criteria except the \\(\\geqslant\\)2-jet requirement; the \\(\\mathrm{t}\\bar{\\mathrm{t}}\\) signal dominates the bins with at least two jets.\n",
            "Figure 1: Number of jets in events passing all dilepton selection criteria before the \\(\\geqslant\\)2-jet requirement for all three dilepton modes combined, compared to signal and background predictions"
        ],
        "atlusUrl": "https://cds.cern.ch/record/1303021",
        "paper": "CDS_Record_1303021",
        "paperName": "First Measurement of the Cross Section for Top-Quark Pair Production in Proton-Proton Collisions at $\\sqrt{s}$ = 7 TeV"
    },
    {
        "name": "Figure 2",
        "mentions": [
            "Fig. 2 shows that the kinematics of the selected events are statistically compatible with predictions based on a top-quark mass of 172.5 \\(\\mathrm{GeV}/c^{2}\\), demonstrating the consistency of the selected sample with top-quark pair production.\n",
            "Figure 2: Distribution of the top-quark mass using two different reconstruction methods [35,36], compared with the expected yields from simulated signal-plus-background and background-only hypotheses"
        ],
        "atlusUrl": "https://cds.cern.ch/record/1303021",
        "paper": "CDS_Record_1303021",
        "paperName": "First Measurement of the Cross Section for Top-Quark Pair Production in Proton-Proton Collisions at $\\sqrt{s}$ = 7 TeV"
    }
]

for figure in data:
    print(f"Processing {figure['name']}...")
    # Combine all mentions together
    combined_mentions = " ".join(figure['mentions'])
    # Preprocess texts
    cleaned_text = preprocess_text(combined_mentions)
    # Extract keywords and print out
    keywords = extract_keywords(cleaned_text)
    print(f"Keywords for {figure['name']}: {keywords}")
    print("\n")
