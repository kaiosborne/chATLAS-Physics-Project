import fitz
import re
import numpy as np
from fitz import Rect
from functools import reduce


def save_image(doc, xref,file_name):
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
        pix = fitz.Pixmap(fitz.csRGB, pix)
    print(f'Saving {file_name}')
    pix.save(file_name) # save the image as png

scaleFactor = 1.5
ZOOM = 2

def extractImagesFromPdf(pattern,outputFormat,inputDir,outPutDir):
	doc = fitz.open(inputDir) # open a document

	for pageIndex in range(len(doc)): # iterate over pdf pages
		page = doc[pageIndex] # get the page
		blocks = page.get_text("blocks")
		images = page.get_images()
		drawings = page.get_drawings()
		
		#find matches
		matches = [b for b in blocks if pattern.search(b[4])]

		for i,m in enumerate(matches):
			if i == 0:
				yTop = 0 #dropping some cases somehow, need to look at	
				yBottom = min(m[3],m[1])
			else:
				yTop = max(matches[i-1][1],matches[i-1][3])
				yBottom = min(m[1],m[3])
			
			imageInRange = [i for i in images if yTop <= i[1] <= yBottom]
			for i,img in enumerate(imageInRange):
				fileName = outputFormat +f'{pattern.search(m[4]).group(1)}-{i}-nimage.png'
				save_image(doc, img[0],outPutDir+"\\"+fileName)

			unionOfRec = [d["rect"] for d in drawings if yTop <= d["rect"][1] <= yBottom]

			if unionOfRec != []:
				drawingRec = reduce(Rect.include_rect, unionOfRec)
				fileName = outputFormat +f'{pattern.search(m[4]).group(1)}-dimage.png'
				pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=drawingRec)
				pix.save(outPutDir+"\\"+fileName)
		

pattern = re.compile(r"^Figure 2(\.\d+)?: ")  # the regex pattern
dataDir = "C:\workspace\git-repos\physics-project\direct pdf extraction"
ouputDirOne = "C:\workspace\git-repos\physics-project\direct pdf extraction\ouput 1"
ouputDirTwo = "C:\workspace\git-repos\physics-project\direct pdf extraction\output 2"
nameOne = "jinst8_08_s08003.pdf"
nameTwo = "arXiv_1503.08988.pdf"
extractImagesFromPdf(pattern,"Fig-2",dataDir + "\\" +nameOne,ouputDirOne)
#extractImagesFromPdf(pattern,"Fig-2-",dataDir + "\\" +nameTwo,ouputDirTwo)

#this method will fail under certain circumstances in multiple column files, so its better to use arXiv if possible

