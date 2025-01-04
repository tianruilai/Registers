#####################################
##########LORENZO BRUNO 2022#########
#######SOCIAL REGISTERS DEATHS#######
#####################################

import re, os, time, csv

output_path = r'C:\Users\87208\Documents\Documents\RA\Social register\deaths_new.csv'
csv_file = open(output_path, 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=',')
csv_writer.writerow(['city', 'year', 'last_name', 'female_deaths', 'male_deaths'])
good_cities=[]
female_death = r"((?<=\*)[A-z ]+\-?$)"
male_death = r"([A-Z][a-z ]+$|[a-z]+ [A-Z][a-z ]+&|[A-Z][a-z]+ [A-Z][a-z ]+$)"

stop_condition = r"MARRIED\.? MAIDENS|ast[eo]risk pr[eo]ce[d ]l?e[8si]x? t?h?e? ?bride[' ]?s n[au][nm]e"

def city_check(City:str, Year:str):
    filepath = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output\\" + City + ' '+ Year + ".txt"
    with open(filepath, 'r') as f:
        lines = f.readlines()
    #d_table_check = r"DEATHS OF|DEATHS|DeathS OF"
    d_table_check = "T?he name o[fj] a Woman|T?he name o[fj] a woman|is indicated by an asterisk"
    for line in range(len(lines)):
        lines[line] = lines[line].strip()
        if "Public Domain, Google-digitized" in lines[line] or "Generated at Harvard University" in lines[line] \
                or 'Digitized' in lines[line] or "Original From" in lines[line]:
            lines[line] = ''
        if "â€™" in lines[line]:
            lines[line] = lines[line].replace("â€™", "'")
        if "\\" in lines[line]:
            lines[line] = lines[line].replace("\\", "")
        if "Ã©" in lines[line]:
            lines[line] = lines[line].replace("Ã©", "é")


        #SPACING
        if re.search(r"^[A-Z][a-z][A-Z][a-z]", lines[line]) is None:
            try:
                lines[line]=re.sub(r"(^[A-Z][a-z]+(?![ a-z]))", r"\1 ", lines[line])
            except:
                pass
        else:
            try:
                lines[line]=re.sub(r"(^[A-Z][a-z][a-z]?[A-Z][a-z]+(?![ a-z]))", r"\1 ", lines[line])
            except:
                pass
        try:
            lines[line]=re.sub(r"((?<=\S)(?<!\()(?<![A-Z][a-qs-z])(?<![A-Z][a-z][a-z])(?<!\&)[A-Z][a-z]+)", r" \1", lines[line])
        except:
            pass


    for line in range(len(lines)):
        if re.search(d_table_check, lines[line]) is not None:
            i=1
            good_cities.append(City + ' ' + Year)
            print(City + ' ' + Year)
            while i < 1000:
                if re.search(female_death, lines[line+i]) is not None:
                    dead=re.search(female_death, lines[line+i]).group(1).strip()
                    csv_writer.writerow([City, Year, dead, "1", "0"])
                elif re.search(female_death, lines[line+i]) is None and re.search(male_death, lines[line+i]) is not None:
                    dead=re.search(male_death, lines[line+i]).group(1).strip()
                    csv_writer.writerow([City, Year, dead, "0", "1"])

                if re.search(stop_condition, lines[line+i]) is not None:
                    break
                i+=1

            break


for _, __, files in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output"):
    for f in files:
        city = re.findall(r"[A-z ]+(?= [0-9])", f)[0]
        year = re.findall(r"[0-9]+", f)[0]
        city_check(city,year)

csv_file.close()