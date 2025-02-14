import os
import re
import yake

# path to papers
PAPER_DIR = r"C:\Users\Jiayi\Desktop\project_code\get-mentions_check\test_paperdata"

# extract abstract in latex.txt
def extract_abstract(latex_text):
    abstract_pattern = re.compile(r"\\begin{abstract}(.*?)\\end{abstract}", re.DOTALL)
    match = abstract_pattern.search(latex_text)
    if match:
        return match.group(1).strip()
    return ""

# extract captions in latex.txt
def extract_captions(latex_text):
    caption_pattern = re.compile(r"\\caption{(.*?)}", re.DOTALL)
    captions = caption_pattern.findall(latex_text)
    return " ".join(captions)

def extract_meta_info(meta_info_path):
    with open(meta_info_path, "r", encoding="utf-8") as file:
        meta_info = file.read()
    
    # extract titles
    paper_name_match = re.search(r"PAPER NAME : (.*)", meta_info)
    paper_name = paper_name_match.group(1).strip() if paper_name_match else "Unknown"
    
    # extract URL
    url_match = re.search(r"URL : (.*)", meta_info)
    url = url_match.group(1).strip() if url_match else "Unknown"
    
    return paper_name, url

# extract keywords by yake
def extract_keywords_yake(text, top_n=10):
    # intialize YAKE
    kw_extractor = yake.KeywordExtractor()
    # extract keywors
    keywords = kw_extractor.extract_keywords(text)
    # back to top_n
    return [kw[0] for kw in keywords[:top_n]]

# one paper
def process_paper(paper_folder):
    latex_path = os.path.join(paper_folder, "latex.txt")
    meta_info_path = os.path.join(paper_folder, "meta_info.txt")
    
    # extract meta_info.txt
    paper_name, url = extract_meta_info(meta_info_path)
    
    # extract latex.txt
    with open(latex_path, "r", encoding="utf-8") as file:
        latex_text = file.read()
    
    # extract abstract
    abstract = extract_abstract(latex_text)
    
    # extract captions
    captions = extract_captions(latex_text)
    
    # 
    combined_text = latex_text + " " + captions * 3 
    keywords = extract_keywords_yake(combined_text)
    
    # Return result
    return {
        "paper_name": paper_name,
        "url": url,
        "keywords": keywords,
        "abstract": abstract,
        "captions": captions
    }


def process_paper_library(library_dir):
    results = []
    for root, dirs, files in os.walk(library_dir):
        for dir_name in dirs:
            if dir_name.startswith("CDS_Record_"):  
                paper_folder = os.path.join(root, dir_name)
                if os.path.exists(os.path.join(paper_folder, "latex.txt")) and os.path.exists(os.path.join(paper_folder, "meta_info.txt")):
                    result = process_paper(paper_folder)
                    results.append(result)
    return results

# Save results to file
def save_results(results, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        for result in results:
            file.write(f"Paper Name: {result['paper_name']}\n")
            file.write(f"URL: {result['url']}\n")
            file.write(f"Keywords: {', '.join(result['keywords'])}\n")
            file.write(f"Abstract: {result['abstract']}\n")
            file.write(f"Captions: {result['captions']}\n")
            file.write("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    results = process_paper_library(PAPER_DIR)
    
    # Save result
    save_results(results, "output_yake.txt")
