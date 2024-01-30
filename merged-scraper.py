import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


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
        

class Figure:
    def __init__(self,imageUrl,name,legend,paperLoc):
        self.loc = imageUrl + name
        self.name = name
        self.legend = legend
        self.paperLoc = paperLoc

    def printData(self):
        print("---------------------")
        print("Loc: " + self.loc)
        print("Name: " + self.name)
        print("Legend: " + self.legend)
        print("Paper: " + self.paper)

    def downloadFigure(self,createLoc):
        pass

    def findMentionsInPaper(self):
        pass
  

#defines directory with data folders in them on local computer
dataDir = r"C:\workspace\git-repos\physics-project\data"

#finds the folder names
folders = os.listdir(dataDir)


figures = []

for f in folders:
    imageUrl = scrapImagePageUrl(dataDir + "\\" + f)
    paperImages = extractNameAndLegendsFromSite(imageUrl)

    for i in paperImages:
        figures.append(Figure(imageUrl,i["name"],i["legend"],f))
        figures[-1].printData()

        
    
    
