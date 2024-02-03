import os
import requests
import re
import json
import itertools

#these are the patterns used to identify figures and tables
figPatterns = [r"[Ff]ig. (\d+)",r"[Ff]igures* (\d+)"]
tablePatterns = [r"[Tt]able (\d+)"]

#these are the identifiers for the figures and tables 
figIdentifier = "Figure "
tableIdentifier = "Table "

def getLinesFromFile(folderLoc,file):
    """Program that gets list of file lines from file in folderloc"""
    fileLoc = folderLoc +"\\" + file
    return open(fileLoc,encoding="utf8").readlines()

def extractImageNamesAndMentions(allLines,patterns,identifier):
    """Given a list of patterns, searches through line list and finds all instances, then groups them together"""
    unsortedMentions = []
    #for all lines check if any patterns occur, if they do find number then add number and line to lst
    for line in allLines:
        for p in patterns: 
            if re.search(p, line):
                search = re.search(p, line)
                unsortedMentions.append({"image number":search.group(1), "line":line})
    #sort list into dictionary where key:image numbers, values: list of corresponding line dictionaries
    mentions = { identifier+imageNumb: list(imageDics) for imageNumb, imageDics in itertools.groupby(unsortedMentions, key=lambda x: x["image number"])}
    #converts line dictionaries into line strings and returns 
    return {k: [l["line"] for l in v]  for k, v in mentions.items()}


#defines directory with data folders and output folders on your local computer
dataDir = r"C:\workspace\data-for-project"
outputDir = r"C:\workspace\git-repos\physics-project"

#finds the folder names
folders = os.listdir(dataDir)
    

figures = []
#for all folders find the directory, then try and fetch data from folders
for f in folders:
    folderDir = dataDir + "\\" + f
    
    try:
        latexLinesList = getLinesFromFile(folderDir,file="latex.txt")
        metaLinesList = getLinesFromFile(folderDir,file="meta_info.txt")
    except:
        print("Proper data doesn't exist at: " + str(f))
        continue

    #find atlus url
    atlusUrl = max(metaLinesList[-1].split(),key=len)

    #for given patterns find dictionaries of image data
    figMentionDic = extractImageNamesAndMentions(latexLinesList,figPatterns,figIdentifier)
    tableMentionDic = extractImageNamesAndMentions(latexLinesList,tablePatterns,tableIdentifier)

    #combine these dictionaries
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    #for all data create a list of dictionaries coresponding to image
    for key, mentions in combinedMentionDic.items():
        figures.append({"name": key, "mentions": mentions,"atlusUrl": atlusUrl,"paper": f})


#create json file to store data in
with open(outputDir+"\\"+"generated-data.json", "w") as outfile:
    for fig in figures:
        outfile.write(json.dumps(fig, indent=4))


"""
Stuff that still needs to be done:

- tidy up code, there some bits that are not very clear
- need find out if jsons are approriate for storing this data
- scraping data for cases like fig 3,4,5, hasn't been added yet (may be too complex)
- need to add comments
- folder finding code doesn't just find folders, this creates problems when other files are in the same folder (I shouldn't have to manually delete them)
- need to find the paper name, may be useful to add the abstract as well
- automated testing needs to be implemented

"""
