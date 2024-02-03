import os
import requests
from bs4 import BeautifulSoup
import re
import json
import itertools



def scrapImagePageUrl(folderLocation):
    """Given folder containing file and metadata, uses metadata to find image url """

    #reads meta text file and finds the intermediate url
    with open(folderLocation + "\meta_info.txt")as f:
        intermediateUrl = f.read().split()[-1]

    #uses soup and regular expressions to find image url in intermediate url
    response = requests.get(intermediateUrl)

    soup = BeautifulSoup(response.text, 'html.parser')
    hyperlinkTags = soup.find_all("a")
    
    for i,h in enumerate(hyperlinkTags):
        try:
            hyperlinkTags[i] = re.findall("https*://atlas.web.cern.ch/.*",h["href"])
        except:
            hyperlinkTags[i] = []
   
    return [i for i in hyperlinkTags if i != []][0][0]
    

def extractNameAndLegendsFromSite(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    
    legendData = soup.find_all("td",  class_="legend")

    data = []
    
    for i,d in enumerate(legendData):
        try:
            fileName = d.find_all("a")[0]["href"]
            legendList = [i.strip() for i in re.findall("\n.*",str(d.get_text()))]

            legend = max(legendList,key=len)

            data.append({"name": fileName,"legend": legend})

        except:
            print("The following data has been lost: " + str(d))
            

    return data

def extractData(folderLoc):
    fileLoc = folderLoc +"\\" +"latex.txt"
    return open(fileLoc,encoding="utf8").readlines()

def checkPatterns(patterns, line):
    for p in patterns:
        if bool(re.search(p, line)):
            return True
    return False

def findMentionsInPaper(patterns,data):
    mentions = [] 
    for line in data:
        if checkPatterns(patterns, line):
            mentions.append(line.strip())
    return mentions

def findSearchPatterns(fileName):
    firstLetters = fileName[:3]
    numbers = re.sub(r"\D", "",fileName).lstrip("0")
    if firstLetters == "fig":
        return [r"F*f*igures* " + numbers +"\D",r"F*f*ig. " + numbers +"\D"]
    elif firstLetters == "tab":
        return [r"Table " + numbers]
    else:
        print("Error figure not in format recognised") #improve this
        return []

#defines directory with data folders in them on local computer
#for this to work its needs to be the data file in your repository
dataDir = r"C:\workspace\git-repos\physics-project\data"
outputDir = r"C:\workspace\git-repos\physics-project"

#finds the folder names
folders = os.listdir(dataDir)

figures = []
for f in folders:
    folderLoc = dataDir + "\\" + f
    paperData = extractData(folderLoc)
    imageUrl = scrapImagePageUrl(folderLoc)
    
    paperImages = extractNameAndLegendsFromSite(imageUrl)

    folderFigures = []
    for i in paperImages:
        folderFigures.append({"name/legend": i, "patterns": findSearchPatterns(i["name"])}) #this is messy here
        
    orderedFigures = { name: list(items) for name, items in itertools.groupby(folderFigures, key=lambda x: x["patterns"][0])}
    for pattern, data in orderedFigures.items():
        names = [i["name/legend"]["name"] for i in data]
        legend = data[0]["name/legend"]["legend"]
        mentions = findMentionsInPaper(data[0]["patterns"],paperData)
        figures.append({ "Names": names, "Legend": legend,"Paper name": f ,"Mentions": mentions,
                 "Location": imageUrl}) 



with open(outputDir+"\\"+"generated-data.json", "w") as outfile:
    for fig in figures:
        outfile.write(json.dumps(fig, indent=4))

#should i change name of figure as it also takes tables
#scrapImagePageUrl could be faster as well
#need to find a neat way to deal with the duplicate problem: 3a,3b,.. all have the same data, so could be optimised here
#scrapping data where fig 3,4,5, hasn't been added yet

