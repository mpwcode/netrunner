from fpdf import FPDF
import json
from datetime import datetime
import webbrowser
from PIL import Image
import math
import sys
import sys
import os
import glob
from operator import itemgetter
import tkinter as tk
from tkinter import filedialog

pdf=FPDF()
pdf.add_page()
pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
pdf.set_font('FreeSans','',10)

root = tk.Tk()
root.withdraw()
image_path = filedialog.askdirectory()

file_list = sorted(glob.glob(image_path+'/*.jpg'))

for filename in file_list:
    file = filename.replace(image_path, "")
    card = file.replace("\\", "")
    #cardname = card[:-4]
    card_picture = Image.open(filename)
    card_picture = card_picture.resize((746, 1033))
    card_picture.save(card)

#pdf.output('images.pdf')