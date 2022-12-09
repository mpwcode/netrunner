from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
import sys

pdf=FPDF()
pdf.add_page()
pdf.set_font('Arial','',10)


packfile=open("packs.json","r")
packs=json.load(packfile)
packfile.close()

#for pack in packs:
#    pack["date"]=datetime.strptime(pack["date_release"], '%Y-%m-%d')

for pack in packs:
    pack["date_release"]=str(pack["date_release"])

packs=sorted(packs, key=lambda x: x["date_release"], reverse=True)

x_offset=50
padding=10

for pack in packs:
    top=pdf.y
    pdf.multi_cell(x_offset, 5, pack["name"], 1, 0)
    pdf.x=x_offset+padding
    pdf.y=top
    pdf.multi_cell(x_offset, 5, pack["date_release"],1,0)



pdf.output('packs.pdf')
