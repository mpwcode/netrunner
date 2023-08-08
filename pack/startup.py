from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
import sys
import os
import glob

pdf=FPDF()
pdf.add_page()
pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
pdf.set_font('FreeSans','',10)
cardlist = []

msfile = open("ms.json","r", encoding = 'utf-8')
ms = json.load(msfile)
msfile.close()

cardlist.append(ms)

pdf.multi_cell(150,5,str(cardlist),1,0)
pdf.output('startup.pdf')