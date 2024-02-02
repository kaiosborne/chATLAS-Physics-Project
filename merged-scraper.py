import os
import requests
from bs4 import BeautifulSoup
import re
import json


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
    
        
#holds all the required data of all the figures
class Figure:
    def __init__(self,imageUrl,fileName,legend,paperName,paperData):
        self.loc = imageUrl + fileName
        self.fileName = fileName.strip()
        self.legend = legend
        self.paperName = paperName
        self.paperData = paperData

        self.findSearchPatterns()
        self.findMentionsInPaper()

    def findSearchPatterns(self):
        firstLetters = self.fileName[:3]
        numbers = re.sub("[^0-9]", "",self.fileName[4:-4]).lstrip("0")
        if firstLetters == "fig":
            self.patterns = [r"F*f*igures* " + numbers +"\D",r"F*f*ig. " + numbers +"\D"]
        elif firstLetters == "tab":
            self.patterns = [r"Table " + numbers]
        else:
            print("Error figure not in format recognised")
            self.patterns = []
        

    def printData(self):
        print("---------------------")
        print("Loc: " + self.loc)
        print("Name: " + self.fileName)
        print("Legend: " + self.legend)
        print("Paper name: " + self.paperName)
        print("Mentions: ")
        for x in self.mentions:
            print(x)

    def downloadFigure(self,createLoc):
        #this function should download the figure into the createLoc directory
        pass

    def findMentionsInPaper(self):
        self.mentions = [] 
        for line in self.paperData:
            if checkPatterns(self.patterns, line):
                self.mentions.append(line.strip())

    def generateDictionary(self):
        return { "Filename": self.fileName, "Location": self.loc,"Paper name": self.paperName ,"Legend (image site)": self.legend,
                 "Mentions": self.mentions}
  

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
    paperImages = extractNameAndLegendsFromSite(imageUrl) #need to name this better
      
    for i in paperImages:
        figures.append(Figure(imageUrl,i["name"],i["legend"],f,paperData))
        figures[-1].printData()

with open(outputDir+"\\"+"generated-data.json", "w") as outfile:
    for fig in figures:
        outfile.write(json.dumps(fig.generateDictionary(), indent=4))

#should i change name of figure as it also takes tables
#scrapImagePageUrl could be faster as well
#need to find a neat way to deal with the duplicate problem: 3a,3b,.. all have the same data, so could be optimised here
#scrapping data where fig 3,4,5, hasn't been added yet

