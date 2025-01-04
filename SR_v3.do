*********** 
***PART 0***
************

clear
global input "C:\Users\87208\Documents\Documents\RA\Social Register"
global dtapath "$input\dta_output"
global csvpath "$input\csv_output"
cd "$csvpath"


*create empty variables
import delimited "New York 1900.csv", clear varnames(1)
*transform address into string
tostring college grad_year address citytown_correct county_correct state_correct region_correct other_city, replace
drop if clubs_abbr != "99999999"
cd "$dtapath"
save "SR_temp.dta", replace
cd "$csvpath"

local csvfiles: dir . files"*.csv"
di `csvfiles'

foreach file of local csvfiles{
	if "`file'" != "deaths.csv" & "`file'" != "marriages.csv" &   "`file'" != "titles.csv" & regexm("`file'", "score") == 0{
	cd "$csvpath"
	import delimited "`file'", clear varnames(1)
	dis "`file'"
	tostring college grad_year address citytown_correct county_correct state_correct region_correct other_city, replace
	*save "dta outputs\`city'`year'dataset.dta", replace
	cd "$dtapath"
	append using "SR_temp.dta"
	save "SR_temp.dta", replace
	}
}

*trim the variables
foreach var of varlist city title last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name clubs_abbr clubs_extended college address address_original citytown_correct county_correct state_correct region_correct other_city grad_year college{
        replace `var' = strtrim(`var')
		replace `var' = "" if `var' == "."
}



************
***PART 1***
************

****revise family structure
/*
local raw_line = _N
forvalues i = 1(1)`raw_line' {
    if (last_name[`i']== "Juniors" | last_name[`i']== "Jo" | last_name[`i']== "Je" | last_name[`i']== "Jun" | last_name[`i']== "Jan" | last_name[`i']== "Jens" | last_name[`i']== "Jors"|last_name[`i']== "Jiors") {
        replace household_id = household_id[`i'+1] in `i'
        replace last_name = last_name[`i'+1] in `i'
		replace household_structure = 5
	}
}

local N = _N
forvalues j = 1(1)`N' {
    if (last_name[`j']== "Miss" | last_name[`j']== "Misses" | last_name[`j']== "Mr") {
        replace household_id = household_id[`j'+1] if _n == `j'
        replace last_name =  last_name[`j'+1] if _n == `j'
		replace household_structure = 3
    }
}
*/

************
***PART 2***
************
clear
cd "$input"

import delimited "csv_output\titles.csv", clear varnames(1)
duplicates drop
save "dta_output\titles.dta", replace
use "dta_output\SR_temp.dta", clear

merge m:1 title using "dta_output\titles.dta", keepusing(correct_title)
order correct_title, after(title)
generate length = strlen(title)

*count how many repeated mismatched wrong titles we have
duplicates tag title if _merge == 1, generate(dupl)
gsort + _merge - dupl - length
drop if _merge == 2
drop _merge

*eventually, drop hh_middle_names and rename midtrim hh_middle_names
*replace hh_middle_names = strtrim(hh_middle_names)

/*
Replace wrong titles
*/

replace correct_title = "Mr&Mrs" if title == `"NEN""'
replace correct_title = "Mr&Mrs" if title == `"NIN""'

*these may be subject to errors due to imprecise digitization
replace correct_title = "Mr" if title == "N" | title == "M"
replace correct_title = "Miss" if title == "-" | title == "N-" | title == "M-"
replace correct_title = "Mrs" if title == `"""'

replace correct_title = "Mr" if title == "/"
*this one is particularly tricky because some are "Mr" and some others are "Mrs". We'll use "Mr" because a large share of the involved observations have male names.

drop if title == ":"
drop if last_name == "Ph" | last_name == "Pb" | last_name == "Php" | last_name == "Phone" & household_structure != 1
*we can drop these observations because are almost all phone numbers that have been matched by mistake

replace correct_title = "Mr&Mrs" if title == "M&M'"

drop if title == "."
*these observations have been matched by mistake (should work with python to avoid this matching)

replace correct_title = "Mr&Mrs" if title ==  `"NAN""'
replace correct_title = "Mr" if title == "'"
replace correct_title = "Mr" if title == "N*"

***problem: lines with Misses or Msrs (Juniors also) have different structures: we should either change the matching patterns for such lines using python or drop the observations. Title "y" means Msrs (Y also?)

replace correct_title = "Mr&Mrs" if title == "M&Mâ€œ"
replace correct_title = "Mr&Mrs" if title == "M&N**"
replace correct_title = "Mr&Mrs" if title ==  `"NEX""'
replace correct_title = "Mr&Mrs" if title ==  "N&N**"
replace correct_title = "Mr&Mrs" if title ==  "N&N"
replace correct_title = "Miss" if title == "Mia"
replace correct_title = "Miss" if title == "Mise"

replace correct_title = "Mr" if title == "|"
*this is particularly inconsistent

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
*replace correct_title = "Mr&Mrs" if correct_title == "" & strpos(title, "NIN") > 0

*generalized title correction
replace correct_title = "Mr&Mrs" if correct_title == "" & regexm(title, `"[A-Z][A-z][A-z][^A-z]|[A-Z][A-Z][A-Z]?|[A-Z][a-z][A-Z][a-z]"') == 1 & strlen(title) < 11

replace correct_title = "Mrs" if correct_title == "" & regexm(title, `"^[A-Z0-9][\"\*\™]"') == 1
replace correct_title = "Mr" if correct_title == "" & regexm(title, "[A-Z]\'") == 1
replace correct_title = "Mr" if correct_title == "" & regexm(title, "[a-z]\'") == 1 & strlen(title) < 5
replace correct_title = "Miss" if correct_title == "" & regexm(title, "[A-Z][a-z]?-") & strlen(title) < 11
replace correct_title = "Miss" if correct_title == "" & regexm(title, "Mi[a-z][a-z]") & strlen(title) == 4

***not sure
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

*drop remaining Juniors 
drop if last_name == "Juniors" | last_name == "Jo" | last_name == "Je" | last_name == "Jun" |last_name == "Jan" | last_name == "Jens"|last_name== "Jors" |  last_name == "Other" | last_name == "Jis"| last_name == "Ji" | last_name == "Jin" 

*drop their precendent
replace spouse_last_name = "" if spouse_name == "late"
replace spouse_middle_names = "" if spouse_name == "late"
replace spouse_name = "" if spouse_name == "late"

*some more cleaning
split middle_names, parse(" ")
egen new_middle_names = concat(middle_names2-middle_names32), punct(" ")
gen clean_for_title = 1 if (first_name == "Miss" | first_name == "Mr" | first_name == "Mrs" | first_name == "Msrs" | first_name == "Misses" | first_name == "The Misses")

replace title = first_name if clean_for_title == 1
replace first_name = middle_names1 if clean_for_title == 1
replace middle_names = new_middle_names if clean_for_title == 1
drop middle_names1-middle_names32 new_middle_names clean_for_title

gen new_suffix = regexs(1) if regexm(middle_names,"([2-3]d|[4-6]th)")
replace suffix = new_suffix if new_suffix != ""
replace middle_names = ustrregexra(middle_names, "([2-3]d|[4-6]th)", "",1) if new_suffix != ""
drop new_suffix

drop if regexm(middle_names,"^(Jan|Feb|Mar|Mch|Mcn|Apr|May|Jun|Jul|Jly|Aug|Sep|Oct|Nov|Dec) ") & household_structure != 1
drop if title == ","
replace middle_names = regexr(middle_names, "av'd.*", "")
replace middle_names = regexr(middle_names, "ab'd.*", "")
replace middle_names = regexr(middle_names, "Ph.*", "")
drop if (regexm(last_name, "^[0-9]+$") |regexm(first_name, "^[0-9]+$") | regexm(middle_names, "^[0-9]+$") |regexm(first_name, "'")) & household_structure != 1
drop if (last_name == "The" | first_name == "The"| last_name == "SOCIAL"|last_name == "Social"| last_name == "NEW" | last_name == "New" | first_name == "Club" | first_name == "club" | first_name == "Co" | last_name == "Hathi" | last_name == "See"  | last_name == "see" | last_name == "due") & household_structure != 1
drop if (strlen(last_name) <3 | (strlen(last_name) == 3 & regexm(last_name, "^[A_Z]+$"))) & household_structure != 1
drop if last_name == "Miss"| last_name == "Mr" | last_name == "Mrs"| last_name == "Msrs" | last_name == "Misses" | last_name == "The Misses"
drop if regexm(last_name, "Ph") & regexm(title, "[0-9][0-9]")
drop if first_name == ""

*drop if middle_names == "Miss"| middle_names == "Mr" | middle_names == "Mrs"| middle_names == "Msrs" | middle_names == "Misses" | middle_names == "The Misses"
*drop if middle_names=="" & first_name == ""

replace spouse_middle_names=subinstr(spouse_middle_names, "- ", "",.)
replace spouse_middle_names=subinstr(spouse_middle_names, "-","",.) if regexm(spouse_middle_names, "-$")
replace middle_names = subinstr(middle_names, "*", "",.)
replace first_name = subinstr(first_name, "*", "",.)

*after the cleaning is over:
replace title = strtrim(title)
foreach var of varlist last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name suffix spouse_lastsurname{
		replace `var' = "" if `var' == ""| `var' == "."
}
gsort - city - year + household_id+ household_structure + last_name + first_name

*generate female dummy
gen female = 2
replace female = 1 if (correct_title=="Miss" | correct_title == "Misses" | correct_title=="Mrs") &  (spouse_name == "" & spouse_last_name == "" & spouse_middle_names == "")
replace female = 0 if correct_title == "Msrs"| correct_title == "Dr"| correct_title == "Lt"| correct_title == "Gen"| correct_title == "Ct"| correct_title == "Hon"| correct_title == "Capt"| correct_title == "Maj"| correct_title == "Col"| correct_title == "BrigGen"|correct_title=="Cdr"| correct_title=="Ens"|correct_title == "Lt&Cdr"| correct_title == "Rev"| correct_title == "Mr"| correct_title == "Mr&Mrs"| correct_title == "Dr&Mrs"| correct_title == "Lt&Mrs"| correct_title == "Gen&Mrs"| correct_title == "Ct&Ctss"| correct_title == "Hon&Mrs"| correct_title == "Capt&Mrs"| correct_title == "Maj&Mrs"| correct_title == "Col&Mrs"|correct_title=="Crd&Mrs"|correct_title=="LtCol&Mrs"| correct_title == "BrigGen&Mrs"| correct_title == "Judge&Mrs"| spouse_name != ""| spouse_last_name != ""| spouse_middle_names != "" 
label define female 0 "Male" 1 "Female" 2 "Uncertain"
*generate widow dummy
gen widow = 2
replace widow = 1 if (spouse_name != "" | spouse_last_name != ""| spouse_middle_names != "") & (correct_title == "Mr" | correct_title == "Mrs"| correct_title == "Dr"| correct_title == "Lt"| correct_title == "Rev"| correct_title == "Col"| correct_title == "Capt"| correct_title == "Maj"| correct_title == "Gen"| correct_title == "Ct"| correct_title == "Hon"| correct_title == "Capt"| correct_title == "Maj"| correct_title == "Col"| correct_title == "BrigGen")
replace widow = 0 if ((spouse_name == "" & spouse_last_name == "" & spouse_middle_names == "") & (correct_title == "Mr" | correct_title == "Dr"| correct_title == "Lt"| correct_title == "Rev"| correct_title == "Col"| correct_title == "Capt"| correct_title == "Maj"))| correct_title == "Mr&Mrs"
replace female = 1 if widow == 1
label define widow 0 "Not Widow" 1 "Widow" 2 "Uncertain"
*generate marriage dummy
gen married = (spouse_name != "" | spouse_middle_names != "" | spouse_last_name != "") 
label define married 0 "Not married" 1 "Married" 2 "Uncertain"
*some more cleaning
label define household_structure 0 "None" 1 "Head" 2 "Spouse" 3"Juniors" 4 "Others" 5 "OtherswithIndent"
label values household_structure household_structure
rename title original_title
rename correct_title title
order original_title, last
order year, first
order city, before(year)
drop dupl
drop length

save "dta_output\Social Registers v3.dta", replace


************
***PART 3***
************
clear
cd "$csvpath"
*`

import delimited "deaths.csv", clear varnames(1)
collapse(sum) female_deaths male_deaths, by(city year last_name)
drop if last_name == "Original from"

cd "$dtapath"
save "deaths.dta", replace

use "Social Registers v3.dta", clear

merge m:1 city year last_name using "deaths.dta", keepusing(female_deaths male_deaths)

bys city year last_name: egen total_deaths = sum(died)
gen reported_deaths = female_deaths+male_deaths
replace reported_deaths = 0 if reported_deaths == .

gen survived = 2
replace survived = 1 if died == 0 & total_deaths >= reported_deaths
replace survived = 0 if died == 1

drop if _merge == 2
drop died female_deaths male_deaths total_deaths reported_deaths _merge
drop if city == ""

label define deaths 0 "Dead" 1 "Alive" 2 "Uncertain"
label values survived deaths

save "Social Registers v3.dta", replace


cd "$csvpath"
import delimited "marriages.csv", clear varnames(1)

gen just_married = 1
duplicates drop
cd "$dtapath"
save "marriages.dta", replace

use "Social Registers v3.dta", clear
merge m:1 city year last_name spouse_last_name using "marriages.dta", keepusing(just_married)
replace just_married = 0 if just_married == .
replace married = 1 if just_married == 1
drop if _merge == 2
drop _merge

*Drop the duplicated record of newly married couples. Some are caught by the text in the main book, some are caught by the marriage list in the appendix.
drop if new_marriage == 1
drop if just_married == 1 &  (title == "Miss"|title == "Misses")
drop new_marriage

rename foreign foreign_original
gen foreign = (foreign_original!="No")
order foreign_original, last
order original_title, last

***Clean the school
split college, parse(,)
split grad_year, parse(,)
split clubs_abbr, parse(,)
split clubs_extended, parse(,)
foreach var of varlist college1 college2 college3 {
    replace `var' = regexr(`var', "Graduate", "")
    replace `var' = regexr(`var', "[0-9]+", "")
}
foreach var of varlist college* grad_year* clubs_extended* clubs_abbr*{
        replace `var' = strtrim(`var')
		replace `var' = "" if `var' == "."
}

***Clean the address
replace state_correct = "" if state_correct == "Colorado" |state_correct == "Oregon" |state_correct == "Arkansas"

gen spouse_suffix = ""
gen last_surname = ""


gsort + city + year + household_id+ household_structure + last_name + first_name
compress

save "Social Registers v3.dta", replace



************
***PART 4***
************

cd "$dtapath"
*transform to short format
drop if spouse_name == "" & spouse_last_name == "" & spouse_middle_names == ""
save "Social Registers v3 Short.dta", replace
replace spouse_suffix = suffix
replace suffix = ""
replace last_surname = spouse_lastsurname
replace last_surname = ""
gen spouse_name2 = first_name
gen spouse_last_name2 = last_name
gen spouse_middle_names2 = middle_names
replace first_name = spouse_name
replace middle_names = spouse_middle_names
replace last_name = spouse_last_name
replace spouse_name = spouse_name2
replace spouse_middle_names = spouse_middle_names2
replace spouse_last_name = spouse_last_name2
drop spouse_name2 spouse_last_name2 spouse_middle_names2
replace household_structure = 2
replace female = 1
foreach var of varlist clubs_abbr clubs_extended* clubs_abbr* college* grad_year*{
            replace `var' = ""
        }
save "Social Registers v3 Short.dta", replace

append using "Social Registers v3.dta"

*revise the death for widows
replace survived = 0 if widow == 1 & household_structure != 2
replace widow = 0 if widow == 1 & household_structure != 2
order spouse_name spouse_middle_names spouse_last_name, before (clubs_abbr)
gsort + city + year + household_id+ household_structure + last_name + first_name
compress
save "Social Registers_long_v3.dta", replace  
export delimited "Social Registers_long_v3.csv", replace

