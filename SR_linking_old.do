*******************
****Tianrui Lai****
*****July 2023*****
*******************

**Specify the path
clear all
cd "C:\Users\87208\Documents\Documents\RA\Social register\dta_output"

use "Social Registers_long_v3.dta"
recast str20 middle_names, force
keep if city == "New York"
foreach var of varlist last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name suffix spouse_lastsurname{
		replace `var' = "none" if `var' == "None"
		replace `var' = "none" if `var' == ""
}
foreach var of varlist college college1 college2 college3 address{
		replace `var' = "none" if `var' == ""
		replace `var' = "none" if `var' == "."
}
**Revise the  dummy for the possible mispelling of titles
replace female = 2 if title=="Miss" | title == "Msrs" | title == "Misses" | title=="Mrs"| title == "Mr"

********************************
**** Generate individual ids****
********************************

****Step 1:Assign id by last_name, first_name, middle_initial, suffix, and spouse_last_name (to those non-duplicated)
gen middle_initial = regexs(1) if regexm(middle_names, "(^[A-Za-z])")

egen person_id_raw =  group(first_name last_name middle_initial suffix )
duplicates tag year person_id_raw, gen (register_duplicate)
tab register_duplicate
bys person_id_raw: egen all_duplicate = sum(register_duplicate)
tab all_duplicate

egen person_id_new = group(first_name last_name middle_initial suffix spouse_last_name )
duplicates tag year person_id_new, gen (register_duplicate_new)
tab register_duplicate_new
bys person_id_raw: egen all_duplicate_new = sum(register_duplicate_new)
tab all_duplicate_new

**Drop the observations with duplicated information
duplicates drop year person_id_new spouse_name spouse_middle_names if (spouse_name != "none" | spouse_middle_names != "none"| spouse_last_name != "none") & household_structure != 1, force
duplicates drop year person_id_new address college if spouse_name == "none" & spouse_middle_names == "none" & spouse_last_name =="none" & household_structure != 1, force

**Store the duplicated people separatey
gen matched = 0
gen person_id_new2 = 0
preserve
keep if all_duplicate_new > 0
distinct person_id_new
save "Social Registers New York additional.dta", replace
restore

***Step2: Group the people by names and spouse names, and then try match the groups without spouses to other groups by address and college.
drop if all_duplicate_new > 0
distinct person_id_new
gen nospouse = (spouse_name == "none" & spouse_middle_names == "none"  & spouse_last_name == "none")
save "Social Registers New York.dta", replace
**First use address to match. Generate address group by firstname, lastname, middleinitial, suffix, and address. The id start from 1.
egen address_id = group(person_id_raw address)
replace address_id =  0 if address == "none"

**2.1 Put aside the address group where more than two spouse groups are matched together
**count the number of matches within each group 
gsort person_id_raw address_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_id[`i'] != 0 & address_id[`i'] == address_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new[`i'- 1] in `i' 
    }
}
gsort person_id_raw address_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_id[`i'] != 0 & address_id[`i'] == address_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new)
replace matched_num = 0 if matched_id == 0
bys address_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY address additional.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "Social Registers New York.dta", replace

**2.2 Match the address group with one nospouse group and one spouse group
**Keep the ones having overlapping address
**Assign the address to all matched non-spouse person
bys address_id: gen numall = _N
bys address_id: egen numnospouse = sum(nospouse)
preserve
drop if address == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
duplicates drop person_id_new, force
rename address newaddress
keep person_id_new newaddress
save "NY address.dta", replace
restore
merge m:1 person_id_new using "NY address.dta"
replace newaddress = address if newaddress == ""
drop address_id
egen address_id = group(person_id_raw newaddress)
drop _merge
save "Social Registers New York.dta", replace
**Assign the same person id to all matched groups
preserve
drop if address == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop person_id_raw, force
replace nospouse = 1
rename person_id_new idnew
keep idnew address_id nospouse
save "NY person.dta", replace
restore
merge m:1 address_id using "NY person.dta"
**Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newaddress address_id idnew nospouse numall numnospouse year_dupl
distinct person_id_new
save "Social Registers New York.dta", replace

**2.4 Match the address group where one nospouse group is matched with more than one spouse group, if they have the same college and have no duplication in years.
use "NY address additional.dta", clear
egen address_college_id = group(address_id college1)
replace address_college_id = 0 if college1 ==  "none"
gsort address_id address_college_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_college_id[`i'] != 0 & address_college_id[`i'] == address_college_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new[`i'- 1] in `i' 
    }
}
gsort person_id_raw address_college_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_college_id[`i'] != 0 & address_college_id[`i'] == address_college_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new)
replace matched_num = 0 if matched_id == 0
bys address_college_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY address additional2.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "NY address additional.dta", replace
**Keep the ones having overlapping address
**Assign the address to all matched non-spouse person
bys address_college_id: gen numall = _N
bys address_college_id: egen numnospouse = sum(nospouse)
preserve
drop if college1 == "none" | address == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
duplicates drop person_id_new, force
rename address newaddress
rename college1 newcollege
keep person_id_new newaddress newcollege
save "NY address.dta", replace
restore
merge m:1 person_id_new using "NY address.dta"
replace newaddress = address if newaddress == ""
replace newcollege = college1 if newcollege == ""
drop address_college_id
egen address_college_id = group(person_id_raw newaddress newcollege)
drop _merge
save "NY address additional.dta", replace
**Assign the same person id to all matched groups
preserve
drop if college1 == "none" | address == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop address_id, force
replace nospouse = 1
rename person_id_new idnew
keep idnew address_college_id nospouse
save "NY person.dta", replace
restore
merge m:1 address_college_id using "NY person.dta"
**Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newaddress address_id idnew numall numnospouse address_college_id newcollege year_dupl 
append using "NY address additional2.dta"
append using "Social Registers New York.dta"
distinct person_id_new
save "Social Registers New York.dta", replace

**2.5 Second use college to match. Repeat the same using colleges and then address.
egen college_id = group(person_id_raw college1)
replace college_id = 0 if college1 == "none"
**count the number of matches within each group 
gsort person_id_raw college_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & college_id[`i'] != 0 & college_id[`i'] == college_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new[`i'- 1] in `i' 
    }
}
gsort person_id_raw college_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & college_id[`i'] != 0 & college_id[`i'] == college_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new)
replace matched_num = 0 if matched_id == 0
bys college_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY college additional.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "Social Registers New York.dta", replace
**Keep the ones having overlapping college
**Assign the college to all matched non-spouse person
bys college_id: gen numall = _N
bys college_id: egen numnospouse = sum(nospouse)
preserve
drop if college == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
drop if matched == 1
duplicates drop person_id_new, force
rename college newcollege
keep person_id_new newcollege
save "NY college.dta", replace
restore
merge m:1 person_id_new using "NY college.dta"
replace newcollege = college if newcollege == ""
drop college_id
egen college_id = group(person_id_raw newcollege)
drop _merge
save "Social Registers New York.dta", replace
**Assign the same person id to all matched groups
preserve
drop if college == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop person_id_raw, force
replace nospouse = 1
rename person_id_new idnew
keep idnew college_id nospouse
save "NY person.dta", replace
restore
merge m:1 college_id using "NY person.dta"
**Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newcollege college_id idnew nospouse numall numnospouse year_dupl
append using "NY college additional.dta"
distinct person_id_new
save "Social Registers New York.dta", replace

*** Step 3: Match the people having duplications in names and spouse surnames in one register to other other non-duplicated people, and reassign the same id to them.
**First try to use the full middle names
use "Social Registers New York additional.dta", clear
gen duplicate = (register_duplicate_new > 0)
gen person_id_temp = person_id_new
replace person_id_temp = 0 if duplicate == 1
egen middlename_id = group(person_id_new middle_names)
duplicates tag middlename_id year, gen (dupl_year)
tab dupl_year
gen dupl = (dupl_year > 0)
bys person_id_new: gen dupl_all = sum(dupl)
tab dupl_all
preserve
keep if dupl_all > 0
drop dupl_year dupl_all dupl
save "Social Registers New York additional2.dta", replace
restore
keep if dupl_all == 0
drop dupl_year dupl_all dupl
gsort middlename_id -person_id_temp 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & middlename_id[`i'] == middlename_id[`i'-1] &person_id_temp[`i'] == 0){
replace person_id_temp = person_id_temp[`i'-1] in `i' if _n > 1
	}
}
save "Social Registers New York additional.dta", replace
**Second try to use spouse_name
use "Social Registers New York additional2.dta", clear
egen spouse_id = group(person_id_new spouse_name)
duplicates tag spouse_id year, gen (dupl_year)
tab dupl_year
gen dupl = (dupl_year > 0)
bys person_id_new: gen dupl_all = sum(dupl)
tab dupl_all
preserve
keep if dupl_all > 0
drop dupl_year dupl_all dupl
save "Social Registers New York additional3.dta", replace
restore
keep if dupl_all == 0
drop dupl_year dupl_all dupl
gsort spouse_id person_id_temp 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & spouse_id[`i'] == spouse_id[`i'-1] &person_id_temp[`i'] == 0){
replace person_id_temp = person_id_temp[`i'-1] in `i' if _n > 1
	}
}
save "Social Registers New York additional2.dta", replace
**Third try to use college
use "Social Registers New York additional3.dta", clear
egen college_id = group(person_id_new college1)
duplicates tag college_id year, gen (dupl_year)
tab dupl_year
gen dupl = (dupl_year > 0)
bys person_id_new: gen dupl_all = sum(dupl)
tab dupl_all
preserve
keep if dupl_all > 0
drop dupl_year dupl_all dupl
save "Social Registers New York additional4.dta", replace
restore
keep if dupl_all == 0
drop dupl_year dupl_all dupl
gsort college_id person_id_temp 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & college_id[`i'] == college_id[`i'-1] &person_id_temp[`i'] == 0){
replace person_id_temp = person_id_temp[`i'-1] in `i' if _n > 1
	}
}
replace person_id_new = person_id_temp if person_id_temp != 0
save "Social Registers New York additional3.dta", replace
**Fourth try to use address
use "Social Registers New York additional4.dta", clear
egen address_id = group(person_id_new address)
duplicates tag address_id year, gen (dupl_year)
tab dupl_year
gen dupl = (dupl_year > 0)
bys person_id_new: gen dupl_all = sum(dupl)
tab dupl_all
preserve
keep if dupl_all > 0
drop dupl_year dupl_all dupl
save "Social Registers New York additional5.dta", replace
restore
keep if dupl_all == 0
drop dupl_year dupl_all dupl
gsort address_id -person_id_temp 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_id[`i'] == address_id[`i'-1] &person_id_temp[`i'] == 0){
replace person_id_temp = person_id_temp[`i'-1] in `i' if _n > 1
	}
}
replace person_id_new = person_id_temp if person_id_temp != 0
save "Social Registers New York additional4.dta", replace

use "Social Registers New York additional.dta", clear
append using "Social Registers New York additional2.dta"
append using "Social Registers New York additional3.dta"
append using "Social Registers New York additional4.dta"
append using "Social Registers New York additional5.dta"
drop duplicate middlename_id spouse_id college_id address_id 
egen person_id = group(person_id_new person_id_temp)
replace person_id_new2 = person_id 
drop person_id
save "Social Registers New York additional.dta", replace

***Step 4: Repeat the same process to match the group without spouses to group with spouses.
gen nospouse = (spouse_name == "none" & spouse_middle_names == "none"  & spouse_last_name == "none")
save "Social Registers New York additional.dta", replace
*First use address to match. Generate address group by firstname, lastname, middleinitial, suffix, and address. The id start from 1.
egen address_id = group(person_id_raw address)
replace address_id =  0 if address == "none"
* Put aside the address group where more than two spouse groups are matched together
*count the number of matches within each group 
gsort person_id_raw address_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_id[`i'] != 0 & address_id[`i'] == address_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new2[`i'- 1] in `i' 
    }
}
gsort person_id_raw address_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_id[`i'] != 0 & address_id[`i'] == address_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new2: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new2)
replace matched_num = 0 if matched_id == 0
bys address_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY address additional.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "Social Registers New York additional.dta", replace

* Match the address group with one nospouse group and one spouse group
*Keep the ones having overlapping address
*Assign the address to all matched non-spouse person
bys address_id: gen numall = _N
bys address_id: egen numnospouse = sum(nospouse)
preserve
drop if address == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
duplicates drop person_id_new2, force
rename address newaddress
keep person_id_new2 newaddress
save "NY address.dta", replace
restore
merge m:1 person_id_new2 using "NY address.dta"
replace newaddress = address if newaddress == ""
drop address_id
egen address_id = group(person_id_raw newaddress)
drop _merge
save "Social Registers New York additional.dta", replace
*Assign the same person id to all matched groups
preserve
drop if address == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop person_id_raw, force
replace nospouse = 1
rename person_id_new2 idnew
keep idnew address_id nospouse
save "NY person.dta", replace
restore
merge m:1 address_id using "NY person.dta"
*Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new2 if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new2 = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newaddress address_id idnew nospouse numall numnospouse year_dupl
distinct person_id_new2
save "Social Registers New York additional.dta", replace

* Match the address group where one nospouse group is matched with more than one spouse group, if they have the same college and have no duplication in years.
use "NY address additional.dta", clear
egen address_college_id = group(address_id college1)
replace address_college_id = 0 if college1 ==  "none"
gsort address_id address_college_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_college_id[`i'] != 0 & address_college_id[`i'] == address_college_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new2[`i'- 1] in `i' 
    }
}
gsort person_id_raw address_college_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & address_college_id[`i'] != 0 & address_college_id[`i'] == address_college_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new2: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new2)
replace matched_num = 0 if matched_id == 0
bys address_college_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY address additional2.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "NY address additional.dta", replace
*Keep the ones having overlapping address
*Assign the address to all matched non-spouse person
bys address_college_id: gen numall = _N
bys address_college_id: egen numnospouse = sum(nospouse)
preserve
drop if college1 == "none" | address == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
duplicates drop person_id_new2, force
rename address newaddress
rename college1 newcollege
keep person_id_new2 newaddress newcollege
save "NY address.dta", replace
restore
merge m:1 person_id_new2 using "NY address.dta"
replace newaddress = address if newaddress == ""
replace newcollege = college1 if newcollege == ""
drop address_college_id
egen address_college_id = group(person_id_raw newaddress newcollege)
drop _merge
save "NY address additional.dta", replace
*Assign the same person id to all matched groups
preserve
drop if college1 == "none" | address == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop address_id, force
replace nospouse = 1
rename person_id_new2 idnew
keep idnew address_college_id nospouse
save "NY person.dta", replace
restore
merge m:1 address_college_id using "NY person.dta"
*Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new2 if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new2 = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newaddress address_id idnew numall numnospouse address_college_id newcollege year_dupl 
append using "NY address additional2.dta"
append using "Social Registers New York additional.dta"
distinct person_id_new2
save "Social Registers New York additional.dta", replace
*Second use college to match. Repeat the same using colleges and then address.
egen college_id = group(person_id_raw college1)
replace college_id = 0 if college1 == "none"
*count the number of matches within each group 
gsort person_id_raw college_id -nospouse
gen matched_id = . 
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & college_id[`i'] != 0 & college_id[`i'] == college_id[`i'- 1] & nospouse[`i'- 1] == 1 & nospouse[`i'] == 0){
        replace matched_id = person_id_new2[`i'- 1] in `i' 
    }
}
gsort person_id_raw college_id -nospouse
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & college_id[`i'] != 0 & college_id[`i'] == college_id[`i'- 1] & nospouse[`i'- 1] == 0 & nospouse[`i'] == 0){
replace matched_id = matched_id[`i'- 1] in `i'
	}
}
replace matched_id = 0 if matched_id == .
bys person_id_new2: egen id = max(matched_id)
replace matched_id = id
drop id
bys matched_id: egen matched_num = nvals(person_id_new2)
replace matched_num = 0 if matched_id == 0
bys college_id: egen num = max(matched_num)
replace matched_num = num if nospouse == 1
drop num
preserve
keep if matched_num > 1
drop matched_num matched_id
save "NY college additional.dta", replace
restore
drop if matched_num > 1
drop matched_num matched_id
save "Social Registers New York additional.dta", replace
*Keep the ones having overlapping college
*Assign the college to all matched non-spouse person
bys college_id: gen numall = _N
bys college_id: egen numnospouse = sum(nospouse)
preserve
drop if college == "none"
keep if numnospouse < numall & numnospouse > 0
drop if nospouse == 0
drop if matched == 1
duplicates drop person_id_new2, force
rename college newcollege
keep person_id_new2 newcollege
save "NY college.dta", replace
restore
merge m:1 person_id_new2 using "NY college.dta"
replace newcollege = college if newcollege == ""
drop college_id
egen college_id = group(person_id_raw newcollege)
drop _merge
save "Social Registers New York additional.dta", replace
*Assign the same person id to all matched groups
preserve
drop if college == "none"
keep if numnospouse < numall & numnospouse > 0
keep if nospouse == 0
duplicates drop person_id_raw, force
replace nospouse = 1
rename person_id_new2 idnew
keep idnew college_id nospouse
save "NY person.dta", replace
restore
merge m:1 college_id using "NY person.dta"
*Do not match those with duplications in the same year
gen person_id_matched = 0
replace person_id_matched = idnew if _merge == 3
replace person_id_matched = person_id_new2 if person_id_matched == 0
duplicates tag person_id_matched year, gen (year_dupl)
replace person_id_new2 = person_id_matched if year_dupl == 0
replace matched = 1 if _merge == 3 & year_dupl == 0
drop _merge person_id_matched newcollege college_id idnew nospouse numall numnospouse year_dupl
append using "NY college additional.dta"
distinct person_id_new2
save "Social Registers New York additional.dta", replace
append using "Social Registers New York.dta"
replace person_id_new2 = 0 if person_id_new2 == .
egen person_id = group(person_id_new person_id_new2)
distinct person_id
replace person_id_new = person_id
drop if person_id_new ==.
save "Social Registers New York.dta", replace

********************************
**** Generate household ids****
********************************
egen household_id_raw = group(year household_id)
drop household_id
**Examine the change of spouses; most of the them are due to errors in OCR, or the inconsistent spelling across years
bys person_id: egen spouse_dupl = nvals(spouse_name spouse_last_name spouse_middle_names)
tab spouse_dupl
bys person_id: egen spouse_dupl_new = nvals(spouse_name)
tab spouse_dupl_new
bys person_id: egen spouse_dupl_new2 = nvals(spouse_last_name)
tab spouse_dupl_new2
drop spouse_dupl spouse_dupl_new spouse_dupl_new2
save "Social Registers New York.dta", replace 

**Prepare the HH head dataset
**Some preliminary cleaning
bys year household_id: egen num_hh = total(household_structure == 1)
drop if num_hh > 1
drop num_hh

preserve
keep if household_structure == 1
egen hhid = group(person_id)
codebook hhid
duplicates tag hhid, gen (hh_duplicate)
tab hh_duplicate 
keep hhid household_id_raw
save "New York HH.dta",replace
restore

merge m:1 household_id_raw using "New York HH.dta"
replace hhid = 0 if _merge == 1
gen in_household = (hhid != 0)
tab in_household
replace household_id_raw = 0 if hhid != 0
egen household_id = group (hhid household_id_raw)
drop _merge household_id_raw hhid in_household
rename household_id hhid
save "Social Registers New York.dta", replace 

****Step 3: Generating the panel data****

/** fill in rhe full panel
xtset person_id year
tsfill, full
gen missing = 1 if household_structure == .
replace missing = 0 if missing == .
sort person_id household_structure
local tol_line= _N
forvalues i = 1(1)`tol_line'{
    if ( `i' > 1 & person_id[`i'] == person_id[`i'-1] & household_structure[`i'] == .){
	foreach var of varlist city title household_structure last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name clubs_abbr clubs_extended college grad_year address address_original citytown_correct county_correct state_correct region_correct other_city  widow married survived just_married foreign foreign_original original_title hhid {
		replace `var' = `var'[`i'-1] in `i' if _n > 1 
		}
	}
}

save "Social Registers New York full.dta", replace
*/

**Track the change of hhid
*Create an hhid for each year
forvalues i = 1(1)60{
	gen hhid`i' = hhid if year == 1894 +`i'
}
gen hhid61 = .
sort person_id year
foreach var of varlist hhid1-hhid61{
	replace `var' = 0 if `var' == .
	bys person_id: replace `var' = sum(`var')
}
*Track the change of household sequentially
forvalues iter = 1/61{
	forvalues i = 1/60{
    replace hhid`i' = hhid`=`i'+1' if hhid`i' == 0
	}
}
forvalues iter = 1/61{
	forvalues i = 2/60{
    replace hhid`i' = hhid`=`i'+1' if hhid`i' == hhid`=`i'-1'
	}
}
sort person_id year
foreach var of varlist hhid1-hhid61{
	replace `var' = . if `var' == 0
}
egen hh_num = rownonmiss(hhid1-hhid31)
tab hh_num

**Check if there are duplicated hhid for the same person
/*
preserve
rename hhid hh_id
gen id = _n
reshape long hhid, i(id) j(num)
bysort id hhid: gen dups = cond(_N==1, 0, 1)
bys id: egen total_dups = total(dups)
tab total_dups
restore
*/

misstable summarize hhid1-hhid60
foreach var of varlist hhid1-hhid61{
	egen count = count(`var')
    if count == 0 {
        drop `var'
    }
	drop count
}

drop if person_id ==  .
order person_id hhid, after(year)
gsort +person_id + year
save "Social Registers New York.dta", replace 

**Create enter and exit variables
bys person_id: egen enter_year = min(year)
bys person_id: egen exit_year = max(year)
gen enter = (enter_year == year)
gen exit = (exit_year == year)
tab enter year, col
tab exit year, col
save "Social Registers_long_NY_v3.dta", replace 
