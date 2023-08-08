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


#sgfile=open(abs_file_path, "r")
#sg=sgfile.readlines()
#sgfile.close()

#for pack in packs:
#    pack["date"]=datetime.strptime(pack["date_release"], '%Y-%m-%d')
packs = {}


#for file in glob.glob(abs_file_path):
#    allfiles=open(file, "r")
#    list = json.load(allfiles)
#    allfiles.close()
#    cards.append(list)
#    pack = file.split('\\')
 #   pack = pack[-1]
#    pack = pack.split('.')
 #   pack = pack[0]
 #   packs[pack]=file
#    #pdf.multi_cell(150,5,pack,1,0)

for file in glob.glob(abs_file_path):
    pack = file.split('\\')
    pack = pack[-1]
    pack = pack.split('.')
    pack = pack[0]
    packs[pack]=file


startup_cycles = ["System Gateway", "System Update 2021", "Borealis"]
more = ["Data and Destiny", "Flashpoint", "Red Sand", "Kitara", "Reign and Reverie", "Magnum Opus", "Ashes"]
standard_cycles = startup_cycles+more

cyclefile = open("cycles.json", "r")
cycles = json.load(cyclefile)
cyclefile.close()

startup_codes = []
standard_codes = []

for cycle in cycles:
    if cycle['name'] in startup_cycles:
        startup_codes.append(cycle['code'])
    if cycle['name'] in standard_cycles:
        standard_codes.append(cycle['code'])
    
packsfile = open("packs.json", "r")
packslist = json.load(packsfile)
packsfile.close()

startup_packs =[]
standard_packs = []

for pack in packslist:
    if pack['cycle_code'] in startup_codes:
        startup_packs.append(pack['code'])
    if pack['cycle_code'] in standard_codes:
        standard_packs.append(pack['code'])
        
cardlistbypack = []

#startup_packs.remove('ph')

for file in startup_packs:
    cardfile = open(packs[file],"r", encoding= 'utf-8')
    cards=json.load(cardfile)
    cardfile.close()
    cardlistbypack.append(cards)

cardlist = []

for list in cardlistbypack:
    for card in list:
        cardlist.append(card)

for card in cardlist:
    if card['type_code']=="identity":
        card['type_code']="1dentity"
    if card['faction_code']=='neutral-runner':
        card['faction_code']='zeutral-runner'
    if card['faction_code']=='neutral-corp':
        card['faction_code']='zeutral-corp'
    if card['side_code']=="corp":
        card['side_code']='xorp'
    if 'keywords' not in card.keys():
        card['keywords']=""

cardlist = sorted(cardlist, key=itemgetter('side_code', 'faction_code', 'type_code', 'keywords', 'stripped_title'))

finallist = []

for card in cardlist:
    if card['title'] not in finallist:
        finallist.append(card['title'])

for card in finallist:
    pdf.multi_cell(150,5,card,1,0)



#pdf.multi_cell(150,5,str(cardlist),1,0)
pdf.output('startup.pdf')
