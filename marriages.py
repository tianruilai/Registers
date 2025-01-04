#####################################
##########LORENZO BRUNO 2022#########
######SOCIAL REGISTERS MARRIAGES#####
#####################################

import re, os, time, csv



output_path = r'C:\Users\87208\Documents\Documents\RA\Social register\marriages_new.csv'
csv_file = open(output_path, 'w', newline='')
csv_writer = csv.writer(csv_file, delimiter=',')
csv_writer.writerow(['city', 'year', 'last_name', 'spouse_last_name'])

#SPLIT LINES INTO SINGLE MARRIAGES
marrsplit = r"(?<![A-z])[fmaonjr](?![A-z])"
stop_condition = r"MARRIED\.? MAIDENS|T?he name o[fj] a Woman|T?he name o[fj] a woman|is indicated by an asterisk"
husband_regex=r"(?<!\*)((?<![A-Z])[a-z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+ ?[A-Z][a-z]+|[A-Z][a-z]+)"
wife_regex=r"(?<=\*)((?<![A-Z])[a-z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+ ?[A-Z][a-z]+|[A-Z][a-z]+)"
merge_marriage=r"^[fmaonjr]"

good_cities=[]
def marriage_check(City:str, Year:str):
    filepath = "C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output\\" + City + ' '+ Year + ".txt"
    with open(filepath, 'r') as f:
        lines = f.readlines()
    #d_table_check = r"DEATHS OF|DEATHS|DeathS OF"
    m_table_check = "ast[eo]risk pr[eo]ce[d ]l?e[8si]x? t?h?e? ?bride[' ]?s n[au][nm]e"
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
            lines[line]=re.sub(r"((?<!\*)(?<=\S)(?<!\()(?<![A-Z][a-qs-z])(?<![A-Z][a-z][a-z])(?<!\&)[A-Z][a-z]+)", r" \1", lines[line])
        except:
            pass




    for line in range(len(lines)):
        if re.search(m_table_check, lines[line]) is not None:
            i=1
            good_cities.append(City + ' ' + Year)
            print(City + ' ' + Year)
            while i > 0:
                if re.search(merge_marriage, lines[line+i]) is not None:
                    j=1
                    while j<10:
                        if re.search(merge_marriage, lines[line+i+j]) is None:
                            lines[line+i]=lines[line+i] + '.' + lines[line+i+j]
                            lines[line+i+j]=''
                            j+=1
                        else:
                            break
                    marriages = re.split(marrsplit, lines[line + i])
                    for m in marriages:
                        if re.search(husband_regex, m) is not None and re.search(wife_regex, m) is not None:
                            wife = re.search(wife_regex, m).group(1).strip()
                            m = m.replace("*" + wife, '')
                            try:
                                husband = re.search(husband_regex, m).group(1).strip()
                                csv_writer.writerow([City, Year, husband, wife])
                            except:
                                pass
                if re.search(stop_condition, lines[line + i]) is not None:
                    break
                i+=1

            break




for _, __, files in os.walk("C:\\Users\\87208\\Documents\\Documents\\RA\\Social register\\text_output"):
    for f in files:
        city = re.findall(r"[A-z ]+(?= [0-9])", f)[0]
        year = re.findall(r"[0-9]+", f)[0]
        marriage_check(city,year)


csv_file.close()