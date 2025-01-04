
import os
import shutil
import re
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import fitz


pdf_dir = Path('C:/Users/87208/Documents/Documents/RA/Social register/pdf_ny/')
out_dir = Path('C:/Users/87208/Documents/Documents/RA/Social register/text_output/')
img_dir = Path('C:/Users/87208/Documents/Documents/RA/Social register/img_output/')

def output_creator(city: str, year:str):

    file = pdf_dir / f"{city} {year}.pdf"
    img_path = img_dir / f"{city} {year}"
    if os.path.exists(img_path):
        shutil.rmtree(img_path)
    os.makedirs(img_path)

    first_page = 30
    last_page = 100

    doc=fitz.open(file)
    imgcount = 0
    for pg in range(doc.pageCount):
        imgcount += 1
        page = doc[pg]
        rotate = int(0)
        # Increase the resolution by 4 times
        zoom_x = 4.0
        zoom_y = 4.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        #generate the path to store image: imagesDir/picname
        pic_name = "pic{}.jpg".format("%03d"%imgcount)
        pic_pwd = os.path.join(img_path, pic_name)
        if not os.path.exists(pic_pwd):
            pm.writeImage(pic_pwd)

    outpages = {}
    tes_cfg = '--psm 6'
    for i, filename in enumerate(os.listdir(img_path)):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(img_path, filename)
            text = pytesseract.image_to_string(image_path, config=tes_cfg)
            outpages[i] = text

    with open(out_dir / f"{city} {year}.txt", 'w', encoding='utf-8', errors='ignore') as f:
        for i, page in outpages.items():
            f.write(f"------------ PAGE {i} ------------")
            f.write("\n")
            f.write(page)
            f.write("\n")
            print("------------------------------------------")
            print(f"Loop count is currently {i}")

    shutil.rmtree(img_path)


for pdfpath,pdfdirs,pdffiles in os.walk(r"C:/Users/87208/Documents/Documents/RA/Social register/pdf_ny"):
    for pdf in pdffiles:
        city = re.findall(r"[A-z ]+(?= [0-9])", pdf)[0]
        year = re.findall(r"[0-9]+", pdf)[0]
        print(city, year)
        output_creator(city, year)

