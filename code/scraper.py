import re
import requests
from bs4 import BeautifulSoup
import json
import os

class HTMLData:
    """Holds the data scrapped from the webpage, isImageData is True if the data is a image we want"""
    def __init__(self,imageData,pictureSite):
        self.directory = pictureSite
        self.imageData = imageData
        self.pngFileName = None
        self.legend = None
        self.isImageData = True

        #runs this function to find file name, also begins process of checking if its imagedata
        self.findFileName()

        
    def findFileName(self):
        """finds filename and does partial check if its image data and runs find legend if check is positive"""
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

            #if data contains an image, find legend; continues checking if its an image
            self.findLegend()
        else:
            self.isImageData = False
            
    def findLegend(self):
        """finds legend and checks if image data, assumes findFileName has already been run in checks"""
        
        #if data contains a legend store it, otherwise change isImageData
        if str(self.imageData["class"][0]) == "legend":
            #get test and find legend
            legendText = self.imageData.get_text()
            newLineList = re.findall("\n.*",str(legendText))
            self.legend = max(newLineList, key=len).strip()
            #having confirmed its an image find actual location
            self.findLocation()
        else:
            self.isImageData = False

    def findLocation(self):
        """Finds the actual location of the file and then runs findDictionary"""
        self.directory = self.directory + self.pngFileName
        self.findDictionary()

    def findDictionary(self):
        """Deduces the dictionary that will be used in the json file"""
        self.dictionary = { "Plots": self.pngFileName, "caption": self.legend, "mentioned": "", "web location": self.directory}

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

def createJsonFile(folder,generatedDataDir):
    """Creates json file of picture data given local folder directory"""

    #finds picture url
    pictureLocation = scrapImagePageUrl(folder)

    #gets data from picture url
    response = requests.get(pictureLocation)

    #uses soup to find data
    soup = BeautifulSoup(response.text, 'html.parser')
    tdElements = soup.find_all('td')

    #puts data in HTMLData structure
    dataList = [HTMLData(e,pictureLocation) for e in tdElements]

    #filters any non image data out of the list
    imageData = [d for d in dataList if d.isImageData]

    #creates json data
    with open(generatedDataDir+"\\"+str(folder.split("_")[-1])+".json", "w") as outfile:
        for d in imageData:
            outfile.write(json.dumps(d.dictionary, indent=4))
    print("Data for: " + folder + ",generated at: " + generatedDataDir)

#defines directory with data folders in them on local computer
dataDir = r"C:\workspace\git-repos\physics-project\data"

#defines where json files should be generated
generatedDataDir = "C:\workspace\git-repos\physics-project\generated-data"

#finds the folder names
folders = os.listdir(dataDir)

#creates the data for each of the folders
for f in folders:
    createJsonFile(dataDir+"\\"+f,generatedDataDir)


