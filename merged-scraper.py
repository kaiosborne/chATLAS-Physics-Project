import os
import requests
import re
import json
import itertools

figPatterns = [r"F*f*ig. (\d+)",r"F*f*igures* (\d+)"]
figIdentifier = "Fig "
tablePatterns = [r"t*T*able (\d+)"]
tableIdentifier = "Table "

def getLinesFromFile(folderLoc,file):
    fileLoc = folderLoc +"\\" + file
    return open(fileLoc,encoding="utf8").readlines()

def extractImageNamesAndMentions(allLines,patterns,identifier):
    unsortedMentions = []
    for line in allLines:
        for p in patterns: #try to clean this up a bit
            if re.search(p, line):
                search = re.search(p, line)
                unsortedMentions.append([search.group(1),line])
    mentions = { identifier+name: list(items) for name, items in itertools.groupby(unsortedMentions, key=lambda x: x[0])}
    return {k: [l[1] for l in v]  for k, v in mentions.items()}


#defines directory with data folders in them on local computer
#for this to work its needs to be the data file in your repository
dataDir = r"C:\workspace\data-for-project"
outputDir = r"C:\workspace\git-repos\physics-project"

#finds the folder names
folders = os.listdir(dataDir)
    

figures = []
for f in folders:
    folderDir = dataDir + "\\" + f
    
    try:
        latexLinesList = getLinesFromFile(folderDir,file="latex.txt")
        metaLinesList = getLinesFromFile(folderDir,file="meta_info.txt")
    except:
        print("Proper data doesn't exist at: " + str(f))
        continue

    atlusUrl = max(metaLinesList[-1].split(),key=len)

    
    figMentionDic = extractImageNamesAndMentions(latexLinesList,figPatterns,figIdentifier)
    tableMentionDic = extractImageNamesAndMentions(latexLinesList,tablePatterns,tableIdentifier)
    combinedMentionDic = {**figMentionDic, **tableMentionDic}

    for key, mentions in combinedMentionDic.items():
        figures.append({"name": key, "mentions": mentions,"atlusUrl": atlusUrl,"paper": f})



with open(outputDir+"\\"+"generated-data.json", "w") as outfile:
    for fig in figures:
        outfile.write(json.dumps(fig, indent=4))


"""
Stuff that still needs to be done:

- look for other search patterns to get more data
- tidy up code, there some bits that are not very clear
- when scrapImagePageUrl add code that scraps directly from text file (already solved in George's code, I adapted part of this code
here) and add this data from json
- need find out if jsons are approriate for storing this data
- scrapImagePageUrl has some efficiency issues
- scraping data for cases like fig 3,4,5, hasn't been added yet (may be too complex)
- need to add comments
- folder finding code doesn't just find folders, this creates problems when other files are in the same folder (I shouldn't have to manually delete them)
- could try and improve efficiency
- need to find the paper name, may be useful to add the abstract as well
- automated testing needs to be implemented
- try and remove some of the try loops, it bad practice to do this

"""
