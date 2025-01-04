####Tianrui Lai####
#####Sep 2023#####

from PyPDF2 import PdfFileReader, PdfFileWriter
import os
import json
import re

pdf_dir = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\pdf_ny\\"
txt_dir = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output\\"
#raw string: treat backlash as literate backlash rather than escape character
#Non-greedy quantifyer: *?
CLUB_DETECT = "(^[A-Z][A-z'’]*)(\s*\.+[acesg0-9\+\.\- ]{3,}?)((\(?[A-Z][a-z'’\.\-\& ]*\)?\s?\&?)+)"
MORE_CLUB_DETECT = "([A-Z][A-z'’]*)(\s*\.+[acesg0-9\+\.\- ]{3,}?)((\(?[A-Z][a-z'’\.\-\& ]*\)?\s?\&?)+)"
SPLIT_CLUB_DETECT = '(' + CLUB_DETECT + ')\s+(' + MORE_CLUB_DETECT + ')'

def extract_club_page(city:str, year:str):
    global pdf_dir, txt_dir

    filedir = txt_dir + city + " " + year + ".txt"
    with open(filedir, errors="ignore") as f:
        lines = f.readlines()
    for l in range(len(lines)):
        lines[l] = lines[l].strip()

    club_page = 0
    clubpage = []


    i = 0
    club_page_found = False
    for line in lines:
        if "--- PAGE " + str(i) + " ---" in line:
            if club_page_found:
                break
            i += 1
        if re.search(r"ABBREVIATION|A'BBREVTATTONS|Club abbreviations\.|CLUB ABBREV|ARBEVIATIONS|ABBREWIATIONS|ABBREWATIONS",line) is not None:
            print("Club page found",f"{i-1}")
            club_page = i-1
            club_page_found = True
            CITY_YEAR_PAGES[city+year] = club_page


    i = 0
    on_club_page = False
    for line in lines:
        if "--- PAGE " + str(i) + " ---" in line:
            if on_club_page:
                break
            i += 1
        if i-1 == club_page:
            clubpage.append(line)
            on_club_page = True


    for line in range(len(clubpage)):
        if "Public Domain, Google-digitized" in clubpage[line] or "Generated at Harvard University" in clubpage[line]:
            clubpage[line] = ''

    clubpage = [item for line in clubpage for item in line.split('|')]
    clubpage = [line.strip() for line in clubpage if line != '']
    clubpage_split = []
    for line in clubpage:
        if re.search(SPLIT_CLUB_DETECT, line):
            full = re.findall(SPLIT_CLUB_DETECT, line)
            clubpage_split.append(full[0][0])
            clubpage_split.append(full[0][4])
        else:
            clubpage_split.append(line)
    clubpage = clubpage_split
    print(clubpage)

    CLUBS = {}
    club_lines = []
    for line in range(len(clubpage)-1):
        #print(line)

        clubs = {}
        #print(f'Processing line {line}')
        club_lines.append(clubpage[line])
        #print(club_lines)

        if "The date following" in clubpage[line+1] or "The first club following" in clubpage[line+1] \
        or "respectively indicate" in clubpage[line+1] or 'Club abbreviations, not included' in clubpage[line+1]\
        or 'Original from' in clubpage[line+1]:
            for c in club_lines:
                full = re.findall(CLUB_DETECT, c)
                if full:
                    complete = full[0][2].strip()
                    complete = complete.strip(".")
                    complete = complete.strip("-")
                    abbr = full[0][0].strip()
                    #print(abbr, complete)
                    if abbr == 'U S A or U S N':
                        abbr = 'U S A'
                        abbr1 = 'U S N'
                        clubs[abbr1] = complete
                    if abbr == 'U. S. A. or U. S. N.':
                        abbr = 'U. S. A.'
                        abbr1 = 'U. S. N.'
                        clubs[abbr1] = complete
                    if abbr == 'USA or USN':
                        abbr = 'USA'
                        abbr1 = 'USN'
                        clubs[abbr1] = complete
                    if abbr == "V'":
                        abbr = "Y'"
                    if "1" in abbr:
                        abbr = abbr.replace("1", "'")
                    clubs[abbr] = complete
                    #print(clubs)


            CLUBS[city] = clubs
            break

    for c in citylist:
        if c not in CITY_CLUBS:
            CITY_CLUBS[c] = {}
        for key1 in CLUBS:
            if c in key1:
                for key2 in CLUBS[key1]:
                    CITY_CLUBS[c][key2] = CLUBS[key1][key2]

##Loop over the registers

citylist=["New York"]
CITY_CLUBS = {}
CITY_YEAR_PAGES = {}

for _, __, files in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output"):
    for f in files:
        city = re.findall(r"[A-z ]+(?= [0-9])", f)[0]
        year = re.findall(r"[0-9]+", f)[0]
        extract_club_page(city, year)


with open("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\city_clubs.txt", 'a+', errors='ignore') as f:
    json_str = json.dumps(CITY_CLUBS, ensure_ascii=False)  # This prevents the json from using escape sequences for unicode characters
    modified_str = json_str.replace('’', "'")
    f.write(modified_str)

with open("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\city_clubs_page.txt", 'a+', errors='ignore') as f:
    json_str = json.dumps(CITY_YEAR_PAGES, ensure_ascii=False)
    modified_str = json_str.replace('’', "'")
    f.write(modified_str)