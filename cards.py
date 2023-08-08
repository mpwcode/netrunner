from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
import sys
import os
import glob




script_path=os.path.abspath(__file__)
script_dir=os.path.split(script_path)[0]
rel_path="pack\/sg.json"
abs_file_path=os.path.join(script_dir, rel_path)

pdf=FPDF()
pdf.add_page()
pdf.set_font('Arial','',10)


sgfile=open(glob.glob(abs_file_path)[0], "r")
sg=json.load(sgfile)
sgfile.close()

#for pack in packs:
#    pack["date"]=datetime.strptime(pack["date_release"], '%Y-%m-%d')


for card in sg:
    top=pdf.y
    pdf.multi_cell(x_offset, 5, pack["title"], 1, 0)
    pdf.x=x_offset+padding
    pdf.y=top
    pdf.multi_cell(x_offset, 5, pack["type_code"],1,0)
    pdf.x=(x_offset+padding)*2
    pdf.y=top
    pdf.multi_cell(x_offset, 5, pack["faction_code"],1,0)


pdf.output('cards.pdf')