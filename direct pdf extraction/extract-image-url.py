import fitz
import re
import numpy as np

scaleFactor = 1.5
ZOOM = 2

def extractImagesFromPdf(pattern,outputFormat,inputDir,outPutDir):
	doc = fitz.open(inputDir) # open a document

	for pageIndex in range(len(doc)): # iterate over pdf pages
		page = doc[pageIndex] # get the page
		blocks = page.get_text("blocks")
		
		#find matches
		matches = [b for b in blocks if pattern.search(b[4])]

		for m in matches:
			xLeft = min(m[0],m[2])
			xRight = max(m[0],m[2])
			yTop = min(m[1],m[3]) - scaleFactor*(xRight-xLeft) 
			#this scale factor part needs to be found accurately
			yBottom = min(m[1],m[3]) 

			if yTop < 0:
				yTop = 0

			pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=fitz.Rect(xLeft,yTop,xRight,yBottom))
			pix.save(outPutDir+"\\"+ outputFormat +f'{pattern.search(m[4]).group(1)}.png')


pattern = re.compile(r"^Figure 2\.?(\d+)?: ")  # the regex pattern
dataDir = "C:\workspace\git-repos\physics-project\direct pdf extraction"
ouputDirOne = "C:\workspace\git-repos\physics-project\direct pdf extraction\ouput 1"
ouputDirTwo = "C:\workspace\git-repos\physics-project\direct pdf extraction\output 2"
nameOne = "jinst8_08_s08003.pdf"
nameTwo = "arXiv_1503.08988.pdf"
extractImagesFromPdf(pattern,"Fig-2-",dataDir + "\\" +nameOne,ouputDirOne)
extractImagesFromPdf(pattern,"Fig-2-",dataDir + "\\" +nameTwo,ouputDirTwo)

#this method will fail under certain circumstances in multiple column files, so its better to use arXiv if possible

