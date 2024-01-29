import re
import requests
from bs4 import BeautifulSoup
import json

class MetaData:
    def __init__(self,imageData,paperDirectory):
        self.paperDirectory = paperDirectory
        #need to add code here that converts the paper directory and gets to webpage that is being scrapped
        #here we are just using the scrapping url for the paper directory
        self.directory = paperDirectory

        self.imageData = imageData
        self.pngFileName = None
        self.legend = None
        self.isImageData = True

        self.findFileName()

        
        
    def findFileName(self):
        #finds hyperlink data
        hyperlinkElements = self.imageData.find_all("a")

        #finds hyperlinks, try added because sometimes a elements don't have links, we don't want this data
        for i in range(len(hyperlinkElements)):
            try:
                hyperlinkElements[i] = hyperlinkElements[i]["href"]    
            except:
                del hyperlinkElements[i]
                self.isImageData = False

        #filters the file types to just pngs
        png =  [h for h in hyperlinkElements if bool(re.search(".*png$",h))]

        #finds png files if they exist in data, otherwise change isImageData
        if png != []:
            self.pngFileName = png[0]

            #if data contains an image, find legend 
            self.findLocation()
        else:
            self.isImageData = False
            
    def findLegend(self):
        #if data contains a legend store it, otherwise change isImageData
        
        if str(self.imageData["class"][0]) == "legend":
            legendText = self.imageData.get_text()
            newLineList = re.findall("\n.*",str(legendText))
            self.legend = max(newLineList, key=len).strip()
            self.findDictionary()
        else:
            self.isImageData = False

    def findLocation(self):
        self.directory = self.directory + self.pngFileName
        self.findLegend()

    def printInfo(self):
        print("----------------------------------------------")
        print("Filename = " + str(self.pngFileName))
        print("Legend = " + str(self.legend))
        print("File Location = " + self.directory)

    def findDictionary(self):
        self.dictionary = { "Plots": self.paperDirectory, "caption": self.legend, "mentioned": "", "web location": self.directory}

site = 'https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/EXOT-2014-17/'

response = requests.get(site)

soup = BeautifulSoup(response.text, 'html.parser')
tdElements = soup.find_all('td')

dataList = [MetaData(e,site) for e in tdElements]
imageData = [d for d in dataList if d.isImageData]
 
with open("sample.json", "w") as outfile:
    for d in imageData:
        outfile.write(json.dumps(d.dictionary, indent=4))

