from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
import sys
import os
import glob
from operator import itemgetter


script_path=os.path.abspath(__file__)
script_dir=os.path.split(script_path)[0]
rel_path="pack/*"
abs_file_path=os.path.join(script_dir, rel_path)

pdf=FPDF()
pdf.add_page()
pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
pdf.set_font('FreeSans','',10)


packs = []


for file in glob.glob(abs_file_path):
    pack = file.split('.')
    if pack[-1] == 'json':
        packs.append(file)


for pack in packs:
    cardfile = open(pack,"r", encoding= 'utf-8')
    cards=json.load(cardfile)
    cardfile.close()
    for card in cards:
        if card['pack_code'] != 'ph' and card['pack_code'] != 'tdc':
            pdf.multi_cell(150,5,card['title'],1,0)
    



#pdf.multi_cell(150,5,str(cardlist),1,0)

pdf.output('proxynexus1.pdf')
