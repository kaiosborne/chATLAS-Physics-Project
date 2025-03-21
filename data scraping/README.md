# Project Pipeline Documentation

This README explains how to run and understand the scripts provided in this directory.

## Overview

The following scripts should be executed in order to achieve correct results. The final goal is to generate an `EmbeddedDB.json` file, containing structured and searchable data for plots and tables extracted from input papers. This .json file can then be loaded by app_chroma to provide the functioning app. 

---

## Execution Order and Descriptions

### 1. **`getMentionsMathsAbbrevs`**
- **Purpose:** Extracts figures and tables from an input folder (containing subfolders with `LATEX.txt` and `META_INFO.txt`).
- **Outputs:** JSON file with:
  - Captions for each figure/table.
  - Sentences mentioning each figure/table.
  - LaTeX math expressions (first occurrence and context).
  - Abbreviations along with their long-form definitions derived from the overall context.

### 2. **`getMathsDefinitionsAsyncGPT`**
- **Purpose:** Uses OpenAI API (model: `4o-mini`) to interpret LaTeX math expressions.
- **Operation:** Replaces initial contexts with AI-generated definitions in the JSON.

### 3. **`getKeywordsAsyncGPT`**
- **Purpose:** Queries OpenAI API to generate keywords (default: 5) describing each plot/table.
- **Outputs:** Adds generated keywords into the existing JSON.

### 4. **`splitMentions`**
- **Purpose:** Separates the mentions of figures from their captions.
- **Outputs:** Splits existing JSON `mentions` field into distinct `caption` and `mentions` fields.

### 5. **Image Scraping Folder**
- **Purpose:** Scripts here generate JSON files containing image URLs for plots from various input types (CMS, ATLAS Paper, CONF note, etc.).
- **Note:** Distinct scripts exist for different input data types.

### 6. **Merge Folder**
- **Purpose:** Merges individual JSON files (containing image URLs) into the overall figure database.
- **Recommendation:** Consider initially creating separate databases for each input type and merging them later, as scripts are tailored for specific input types.
  - **Potential improvement area:** Generalize merge scripts to handle all input types uniformly.

### At this stage, figures now have associated image links (some may have multiple images).

### 7. **`splitPlots`**
- **Purpose:** Divides figures containing multiple images into separate subplots.
- **Example:** Converts "Figure 7" with multiple images  into "Figure 7 (a), Figure 7 (b)," etc.

### 8. **`replaceTerms`**
- **Purpose:** Expands abbreviations in captions and mentions to their long forms.
- **Note:** This script can be executed anytime in the pipeline after abbreviations are identified.

### 9. **`getGraphTypeLLM`**
- **Purpose:** Downloads and executes the CLIP model locally to classify plot types from predefined categories.
- **Note:** Categories and accuracy are preliminary; refinement is recommended for improved results.

### 10. **`embedding`**
- **Purpose:** Generates embedding matrices for each figure for vector-based searching.
- **Customization:** Embeddings can be tailored to specific aspects (e.g., captions, mentions), impacting search performance.
- **Final Output:** Creates `EmbeddedDB.json`, which can be used with `app_chroma` (located in the App Product folder) for efficient vector-based searches.

---

## Output Files and Folders

- **Final output:** `EmbeddedDB.json`
- **Intermediate outputs:** Saved after each step, useful for debugging and verification.
- **Example outputs:** Refer to `test outputs` folder (run specifically on ATLASPapers for demonstration purposes).
- **Image URLs Folder:** Illustrates URL extraction processes.

---

## Additional Notes
- The merge scripts might share similarities across input types, but the URL extraction scripts are distinct and specialized per input type.

---
