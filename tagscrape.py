##In each of the files, the order is as such:
##TABLE <---- Greenheader, gives class subject, name, cat number
##TABLE <---- Mixed table, has section info headers, then section info in TBODY
##  TR  <---- Section Info Headers, none useful
##  TR  <---- Section info, first visible TD CID. Check to see if BS catches commented line.
##   .  <---- Above repeats for as many sections as there are in the class.
##   .
##   .
##
from bs4 import BeautifulSoup
import os
import json

subjects = ["CIS", "EEC", "ESC"]
sections = []
jsonout = ""

class Section:
    def __init__(self, cid, subject, semester, tag):
        self.cid = cid
        self.subject = subject
        self.semester = semester
        self.tag = tag


for filename in os.listdir('TAGS'):

    if filename.startswith("SUM22") and filename.endswith(".html"):
        semester, tag = filename[:-5].split("_")
        with open(f"TAGS/{filename}") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        
        souptables = soup.find_all("table", width="100%")
        skipnext = False
        for table in souptables:
            if skipnext == True: ##Should be the mixed table. This will already have been processed.
                skipnext = False
                nexttable = table.find_next_sibling("table")
                if nexttable.attrs['width'] != '100%': ##This only happens on nonuseful tables
                    break
                continue
            
            ##New greenheader table.
            skipnext = True
            subject = table.find_all("tr")[1].find_all("td")[2].get_text()
            if subject not in subjects:
                continue
            
            ##Travel to next table to get CID for sections. 
            sectionstable = table.find_next_sibling("table")
            ##Get Sections.
            sectiontrs = sectionstable.find_all("tr")[1:]
            for sectiontr in sectiontrs:
                cid = sectiontr.find_all("td")[1].get_text()
                sect = Section(cid, subject, semester, tag)
                sections.append(sect)

##serialize and dump
jsonout = json.dumps([x.__dict__ for x in sections])
print(jsonout)

with open("SUM22tags.json", "w") as outfile:
            outfile.write(jsonout)
        

