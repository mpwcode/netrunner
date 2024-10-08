from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
import sys
import os
import glob




script_path=os.path.abspath(__file__)
script_dir=os.path.split(script_path)[0]
rel_path="pack/*"
abs_file_path=os.path.join(script_dir, rel_path)

pdf=FPDF()
pdf.add_page()
pdf.set_font('Arial','',10)


#sgfile=open(abs_file_path, "r")
#sg=sgfile.readlines()
#sgfile.close()

#for pack in packs:
#    pack["date"]=datetime.strptime(pack["date_release"], '%Y-%m-%d')
packs = {}

for file in glob.glob(abs_file_path):
    pack = file.split('\\')
    pack = pack[-1]
    pack = pack.split('.')
    pack = pack[0]
    packs[pack]=file
    pdf.multi_cell(150,5,pack,1,0)
    pdf.multi_cell(150,5,file,1,0)

pdf.multi_cell(150,5,str(packs),1,0)
pdf.output('startup.pdf')
