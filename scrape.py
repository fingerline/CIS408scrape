import datetime
import sys
from types import NoneType
from bs4 import BeautifulSoup, NavigableString;
import re
import json
from copy import deepcopy
sys.setrecursionlimit(10000)
semesters = ["SUM22"]
subjects = ["CIS", "EEC", "ESC"]


    
def validate(template, input):

    if input == "TBA":
        return "None", "None"

    frag1 = input.split("-")[0].strip()
    frag2 = input.split("-")[1].strip()

    
    return frag1, frag2

for semester in semesters:
    for subject in subjects:
        persdatastr = semester + subject + "_files/persdata.html"
        with open(persdatastr) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        classnames = soup.select(".bigfont") ##all class headers, have names
        classdicts = []
        for e in classnames:
            class_name = e.getText()
            sections = []
            ##Each class will have one or more SECTIONS. We look through the siblings for what we think are sections.
            for x in e.next_siblings:        
                if isinstance(x, NavigableString):
                    continue
                if "class" in x.attrs:
                    if x.attrs['class'][0] == "bigfont":
                        for section in sections:
                            section['semester'] = semester
                            section['subject'] = subject
                            classdicts.append(section)
                        break
                if "valign" in x.attrs:
                    if(type(x.next_sibling) == NoneType):
                        for section in sections:
                            section['semester'] = semester
                            section['subject'] = subject
                            classdicts.append(section)
                        break
                    if x['valign'] == 'baseline':
                        headlinedetails = {}
                        if len(x.find_all('td')) < 3:
                            if(type(x.next_sibling.next_sibling.next_sibling) == NoneType):
                                for section in sections:
                                    section['semester'] = semester
                                    section['subject'] = subject
                                    classdicts.append(section)
                                break
                            continue 
                        try:
                            st = x.next_sibling.next_sibling.find_all(string=re.compile("Topic:"), recursive = True)
                            if st != []:
                                headlinedetails["specialtopic"]= st[0].text
                        except Exception as ex: print(ex)

                        ##Get Headline
                        headlinetds = [i.get_text().strip() for i in x.find_all('td')]
                        headlinedetails["name"] = class_name

                        headlinetds = headlinetds[2:]
                        
                        if len(headlinetds) > 11:
                            headlinedetails["cid"] = int(headlinetds[0])
                            headlinedetails["sec"] = headlinetds[1]
                            headlinedetails["sess"] = headlinetds[2]
                            headlinedetails["begd"], headlinedetails["endd"] = validate("date", headlinetds[3])
                            headlinedetails["days"] = headlinetds[4].split(",")
                            headlinedetails["begt"], headlinedetails["endt"] = validate("time", headlinetds[5])
                            headlinedetails["room"] = headlinetds[6]
                            headlinedetails["inst"] = headlinetds[7]
                            headlinedetails["comp"] = headlinetds[8]
                            headlinedetails["stat"] = True if headlinetds[10] == "O" else False
                            headlinedetails["enrl"] = int(headlinetds[11].split("/")[0])
                            headlinedetails["capc"] = int(headlinetds[11].split("/")[1])
                        else:
                            headlinedetails["cid"] = int(headlinetds[0])
                            headlinedetails["sec"] = headlinetds[1]
                            headlinedetails["begd"], headlinedetails["endd"] = validate("date", headlinetds[2])
                            headlinedetails["days"] = headlinetds[3].split(",")
                            headlinedetails["begt"], headlinedetails["endt"] = validate("time", headlinetds[4])
                            headlinedetails["room"] = headlinetds[5]
                            headlinedetails["inst"] = headlinetds[6]
                            headlinedetails["comp"] = headlinetds[7]
                            headlinedetails["stat"] = True if headlinetds[9] == "O" else False
                            headlinedetails["enrl"] = int(headlinetds[10].split("/")[0])
                            headlinedetails["capc"] = int(headlinetds[10].split("/")[1])
                            
                        ##secname = x.get_text()
                        ##Look for class data in the dropdown. Cdata stores this.
                        cdata = x.find_next_sibling(attrs={"style":"", "valign":"top"}).find("tbody").find("tbody")
                        desc = x.findNext("b").next_sibling.next_sibling.text
                        headlinedetails["desc"] = desc

                        cdatarows = cdata.select("tr")

                        for row in cdatarows:
                            abe = row.select("td:nth-child(odd)")
                            for cab in abe:
                                if cab.text.isspace() or type(cab.next_sibling) == NoneType:
                                    break
                                headlinedetails[cab.text] = cab.next_sibling.text
                        sections.append(deepcopy(headlinedetails))
                        continue
                else:
                    continue
            

        print(f"done {semester}{subject}")

        jsondata = json.dumps(classdicts)
        outfilestr = "json/" + semester + subject + ".json"
        with open(outfilestr, "w") as outfile:
            outfile.write(jsondata)
