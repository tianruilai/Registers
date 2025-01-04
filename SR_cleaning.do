**************************
* APPEND RAW CSV OUTPUTS *
**************************
clear
global input "~\Dropbox\registers\data\input\register"
global dtapath "$input\dta outputs"
global csvpath "$input\csv outputs"
global build "~\Dropbox\registers\data\build\registers"
cd "$csvpath"

import delimited "New York1900dataset.csv", clear varnames(1)
drop if clubs_abbr != "99999999"
cd "$dtapath"
save "SR_temp.dta", replace
cd "$csvpath"

local csvfiles: dir . files"*.csv"
di `csvfiles'

foreach file of local csvfiles{
	if "`file'" != "deaths.csv" & "`file'" != "marriages.csv" & "`file'" != "titles.csv"{

	cd "$csvpath"
	import delimited "`file'", clear varnames(1)
	*save "dta outputs\`city'`year'dataset.dta", replace
	cd "$dtapath"
	append using "SR_temp.dta"
	save "SR_temp.dta", replace
	}
}

******************************
*MERGE TITLES AND CLEAN NAMES*
******************************
clear
cd "$input"
import delimited "csv outputs\titles.csv", clear varnames(1)
duplicates drop
save "dta outputs\titles.dta", replace
use "dta outputs\SR_temp.dta", clear
merge m:1 title using "dta outputs\titles.dta", keepusing(correct_title)
order correct_title, after(title)
generate length = strlen(title)

*Check the most frequent misspellings in titles
duplicates tag title if _merge == 1, generate(dupl)
gsort + _merge - dupl - length

*Trim middle names
replace middle_names = strtrim(middle_names)
replace title = strtrim(title)

*eventually, drop hh_middle_names and rename midtrim hh_middle_names
*replace hh_middle_names = strtrim(hh_middle_names)

*Clean the most frequent misspellings in titles
replace correct_title = "Mr&Mrs" if title == `"NEN""'
replace correct_title = "Mr&Mrs" if title == `"NIN""'
replace correct_title = "Mr" if title == "N" | title == "M"
replace correct_title = "Miss" if title == "-" | title == "N-" | title == "M-"
replace correct_title = "Mrs" if title == `"""'
replace correct_title = "Mr" if title == "/"
replace correct_title = "Mr&Mrs" if title == "M&M'"
replace correct_title = "Mr&Mrs" if title ==  `"NAN""'
replace correct_title = "Mr" if title == "'"
replace correct_title = "Mr" if title == "N*"
replace correct_title = "Mr&Mrs" if title == "M&Mâ€œ"
replace correct_title = "Mr&Mrs" if title == "M&N**"
replace correct_title = "Mr&Mrs" if title ==  `"NEX""'
replace correct_title = "Mr&Mrs" if title ==  "N&N**"
replace correct_title = "Mr&Mrs" if title ==  "N&N"
replace correct_title = "Miss" if title == "Mia"
replace correct_title = "Miss" if title == "Mise"
replace correct_title = "Mr" if title == "|"
replace correct_title = "Mr&Mrs" if title ==  `"M&Mâ€"'
replace correct_title = "Mr" if title == "l'" | title == "1'"
replace correct_title = "Mr" if title == "Y'" | title == "Y"
replace correct_title = "Mr" if title == `"It""'
replace correct_title = "Miss" if title == "*"
replace correct_title = "Mrs" if title == `"l""' | title ==`"1""'
replace correct_title = "Mr&Mrs" if title ==  `"DEN""'
replace correct_title = "Mr&Mrs" if title ==  `"NN""'
replace correct_title = "Mr&Mrs" if title ==  `"1"*"'
replace correct_title = "Misses" if title == "M."
replace correct_title = "Dr&Mrs" if correct_title == "" & regexm(title, "D[a-z]?\&[A-Z]")
replace correct_title = "Mr&Mrs" if correct_title == "" & strpos(title, "&") > 0
*Problem: lines with Misses or Msrs (Juniors also) have different structures: we should either change the matching patterns for such lines using python or drop the observations. Title "y" means Msrs (Y also?)

*This correction part is more generalized (we're looking at patterns instead of correcting specific misspellings)
replace correct_title = "Mr&Mrs" if correct_title == "" & regexm(title, `"[A-Z][A-z][A-z][^A-z]|[A-Z][A-Z][A-Z]?|[A-Z][a-z][A-Z][a-z]"') == 1 & strlen(title) < 11
replace correct_title = "Mrs" if correct_title == "" & regexm(title, `"^[A-Z0-9][\"\*\™]"') == 1
replace correct_title = "Mr" if correct_title == "" & regexm(title, "[A-Z]\'") == 1
replace correct_title = "Mr" if correct_title == "" & regexm(title, "[a-z]\'") == 1 & strlen(title) < 5
replace correct_title = "Miss" if correct_title == "" & regexm(title, "[A-Z][a-z]?-") & strlen(title) < 11
replace correct_title = "Miss" if correct_title == "" & regexm(title, "Mi[a-z][a-z]") & strlen(title) == 4
replace correct_title = "Mrs" if correct_title == "" & regexm(title, "..?\*") & strlen(title) < 4
replace correct_title = "Mrs" if correct_title == "" & regexm(title, `".?\""') & strlen(title) < 4
replace correct_title = "Mr" if correct_title == "" & regexm(title, `"\'"') & strlen(title) == 2
replace correct_title = "Mr" if correct_title == "" & regexm(title, "[A-Z]r") & strlen(title) == 2
replace correct_title = "Miss" if correct_title == "" & regexm(title, "[NV][a-z]") & strlen(title) == 2
replace correct_title = "Mrs" if correct_title == "" & regexm(title, "[A-Z]â¢")
replace correct_title = "Miss" if correct_title == "" & regexm(title, "[NV][a-z]\*\*?") & strlen(title) <5
replace correct_title = "Miss" if correct_title == "" & regexm(title, "[MNVH][iao][easn]") & strlen(title) <5
replace correct_title = "Rev Dr&Mrs" if title == `"RevD.N""'
replace correct_title = "Mr&Mrs" if correct_title == "" & regexm(title, "[A-Z]\.[A-Z]")

*We can drop the following observations because they are almost all phone numbers that have been erroneously matched
drop if title == ":"
drop if last_name == "Ph" | last_name == "Pb" | last_name == "Php" | last_name == "Phone"
drop if title == "."

*Here we are dropping individuals identified as "Juniors". If we want to keep them we must comment out the next 2 lines.
drop if last_name == "Juniors" | last_name == "Jo" | last_name == "Je" | last_name == "Jun" |last_name == "Jan" | last_name == "Jens"
drop if regexm(last_name, "Ph") & regexm(title, "[0-9][0-9]")

*Minor cleanings
drop if first_name == "Miss" | last_name == "Miss"
replace spouse_middle_names=subinstr(spouse_middle_names, "- ", "",.)
replace spouse_middle_names=subinstr(spouse_middle_names, "-","",.) if regexm(spouse_middle_names, "-$")
replace middle_names = subinstr(middle_names, "*", "",.)
replace first_name = subinstr(first_name, "*", "",.)
replace graduationyear = . if clubs_extended == ""
drop _merge
gsort - city - year + last_name + first_name
rename graduationyear grad_year
replace grad_year = . if clubs_extended == ""
drop if title == ","
rename title original_title
rename correct_title title
order original_title, last
order year, first
order city, before(year)
drop dupl
drop length
replace spouse_middle_names = "" if spouse_middle_names == "None"
replace spouse_name = "" if spouse_name == "None"
replace spouse_last_name = "" if spouse_last_name == "None"

*Create female dummy
gen female = (title=="Miss" | title == "Msrs" | title == "Misses")
gen married = (spouse_last_name != "" | spouse_middle_names != "" | spouse_last_name != "")

*Save the cleaned dataset
save "$build\Social Registers v2.dta", replace

******************************
* MERGE DEATHS AND MARRIAGES *
******************************
clear
cd "$csvpath"
import delimited "deaths.csv", clear varnames(1)
collapse(sum) female_deaths male_deaths, by(city year last_name)
drop if last_name == "Original from"
cd "$dtapath"
save "deaths.dta", replace

*Load the main dataset
use "$build\Social Registers v2.dta", clear

*** Merge Deaths
merge m:1 city year last_name using "deaths.dta", keepusing(female_deaths male_deaths)
bys city year last_name: egen total_deaths = sum(died)

*In some cases, if a person died in the last year, this information is reported next to her name
gen reported_deaths = female_deaths+male_deaths
replace reported_deaths = 0 if reported_deaths == .

*Problem: most of the deaths are reported at the end of the register and only the last name is reported. Because of that, not all the deaths can be imputed with certainty
gen survived = 2
replace survived = 1 if died == 0 & total_deaths >= reported_deaths
replace survived = 0 if died == 1
drop died female_deaths male_deaths total_deaths reported_deaths _merge
drop if city == ""
label define deaths 0 "Dead" 1 "Alive" 2 "Uncertain"
label values survived deaths
save "$build\Social Registers v2.dta", replace

*** Merge Marriages
cd "$csvpath"
import delimited "marriages.csv", clear varnames(1)
gen just_married = 1
replace last_name = strtrim(last_name)
replace spouse_last_name = strtrim(spouse_last_name)
duplicates drop
cd "$dtapath"
save "marriages.dta", replace
use "$build\Social Registers v2.dta", clear
merge m:1 city year last_name spouse_last_name using "marriages.dta", keepusing(just_married)
replace just_married = 0 if just_married == .
drop if _merge == 2
drop _merge
rename foreign foreign_original
gen foreign = (foreign_original!="No")
order foreign_original, last
order original_title, last
drop if female == .
compress

*Save the final dataset
save "$build\Social Registers v2.dta", replace
