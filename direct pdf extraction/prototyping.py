import fitz
import re
import numpy as np
from functools import reduce
from fitz import Rect

PAGE_NUM = 81

def save_image(doc, xref):
    pix = fitz.Pixmap(doc, xref)
    if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
        pix = fitz.Pixmap(fitz.csRGB, pix)
    file_name = f'extracted-image-{xref}.png'
    print(f'Saving {file_name}')
    pix.save(file_name) # save the image as png

loc = "C:\workspace\git-repos\physics-project\direct pdf extraction"
doc = fitz.open(loc + "\\"+ "jinst8_08_s08003.pdf") # open a document
page = doc[PAGE_NUM]
images = page.get_images()
print(images)


ZOOM = 4
print(page.rect)

print('---- Drawings ----')
drawings = page.get_drawings()
print(f'Number of drawings: {len(drawings)}')


rects = [d['rect'] for d in drawings]
union_rect = reduce(Rect.include_rect, rects)
print(f'enlarged rect: {union_rect}')
print(f'Saving page {PAGE_NUM} fragment as PNG')
pix = page.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=union_rect)
pix.save(loc+"\\"+f'page-{PAGE_NUM}-fragment.png')
