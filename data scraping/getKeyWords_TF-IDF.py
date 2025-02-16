import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk

# download stopwords from nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

# Set path for papers
PAPER_DIR = r"C:\Users\Jiayi\Desktop\project_code\get-mentions_check\test_paperdata"

# Customize stopwords
custom_stopwords = set([
    "university", "institution", "organization", "department", "research", "study", "author", "conference", "paper",
    "the", "and", "in", "on", "of", "to", "for", "with", "as", "by", "at", "from", "an", "be", "is", "it", "its", "a", "this", "that",
    "model", "methods", "methodology", "analysis", "algorithm", "system", "data", "results", "technique", "approach", "using", 'usa', 'italy', 'institute' , 'doi', 'arxiv'
    
])

def extract_abstract(latex_text):
    """extract abstract"""
    abstract_pattern = re.compile(r"\\begin{abstract}(.*?)\\end{abstract}", re.DOTALL)
    match = abstract_pattern.search(latex_text)
    return match.group(1).strip() if match else ""

def extract_captions(latex_text):
    """extract caption"""
    caption_pattern = re.compile(r"\\caption{(.*?)}", re.DOTALL)
    return " ".join(caption_pattern.findall(latex_text))

def extract_meta_info(meta_info_path):
    """extract meta info"""
    with open(meta_info_path, "r", encoding="utf-8") as file:
        meta_info = file.read()
    paper_name = re.search(r"PAPER NAME : (.*)", meta_info).group(1).strip() if re.search(r"PAPER NAME : (.*)", meta_info) else "Unknown"
    url = re.search(r"URL : (.*)", meta_info).group(1).strip() if re.search(r"URL : (.*)", meta_info) else "Unknown"
    return paper_name, url

def remove_latex_commands(text):
    """remove latex commands"""
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)  
    text = re.sub(r'\\[a-zA-Z]+', '', text)        
    text = re.sub(r'\{.*?\}', '', text)             
    text = re.sub(r'\\begin\{.*?\}.*?\\end\{.*?\}', '', text, flags=re.DOTALL)  
    return text

def extract_keywords_tfidf(text, top_n=7):
    """extract keywords"""
    stop_words = stopwords.words('english')  
    combined_stopwords = stop_words + list(custom_stopwords)  # combine nltk and custom stopwords

    # Set TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words=combined_stopwords, ngram_range=(1, 3), max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.sum(axis=0).A1 
    sorted_indices = scores.argsort()[::-1] 
    return [feature_names[i] for i in sorted_indices[:top_n]]


def process_paper(paper_folder):
    """"""
    latex_path = os.path.join(paper_folder, "latex.txt")
    meta_info_path = os.path.join(paper_folder, "meta_info.txt")
    
    paper_name, url = extract_meta_info(meta_info_path)
    
    # Load latex.txt
    with open(latex_path, "r", encoding="utf-8") as file:
        latex_text = file.read()
    
    # remove latex commands
    latex_text_cleaned = remove_latex_commands(latex_text)
    
    # extract abstract and captions
    abstract = extract_abstract(latex_text)
    captions = extract_captions(latex_text)
    
    combined_text = f"{latex_text_cleaned} {captions * 3}".lower()  # lower all words

    keywords = extract_keywords_tfidf(combined_text)
    
    return {
        "paper_name": paper_name,
        "url": url,
        "keywords": keywords,
        "abstract": abstract,
        "captions": captions
    }

def process_paper_library(library_dir):
    """all papers in database"""
    results = []
    for root, dirs, _ in os.walk(library_dir):
        for dir_name in dirs:
            if dir_name.startswith("CDS_Record_"):
                paper_folder = os.path.join(root, dir_name)
                required_files = ["latex.txt", "meta_info.txt"]
                if all(os.path.exists(os.path.join(paper_folder, f)) for f in required_files):
                    results.append(process_paper(paper_folder))
    return results

def save_results(results, output_file):
    """save results """
    with open(output_file, "w", encoding="utf-8") as file:
        for result in results:
            file.write(f"Paper Name: {result['paper_name']}\nURL: {result['url']}\n")
            file.write(f"Keywords: {', '.join(result['keywords'])}\n")
            file.write(f"Abstract: {result['abstract']}\nCaptions: {result['captions']}\n\n{'='*50}\n")

if __name__ == "__main__":
    results = process_paper_library(PAPER_DIR)
    save_results(results, "output_tfidf_custom_stopwords.txt")
