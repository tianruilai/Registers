
clear all
cd "C:\Users\87208\Documents\Documents\RA\Social register\dta_output"
*Collapse the long dataset
*use "Social Registers v3.dta"
*collapse the short dataset
use "Social Registers v3 standardized.dta"

***prelimary cleaning
*foreach var of varlist last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name {
*		replace `var' = "None" if `var' == ""
*}
foreach var of varlist last_name first_name middle_names {
		replace `var' = "None" if `var' == ""
}

***drop observations duplicated in each register
duplicates tag city year last_name first_name middle_names, gen (register_duplicate)
tab register_duplicate
keep if register_duplicate == 0

***examine the distribution of reoccurence 
bys city last_name first_name middle_names other_city: gen order = _n
replace order = . if order != 1
bys city last_name first_name middle_names: egen city_dupl = count(order)
tab city_dupl
drop if city_dupl > 2
drop register_duplicate city_dupl order

***generate personal id
replace other_city = "" if other_city == "Englewood"|other_city == "Geneva"|other_city == "Morristown"|other_city == "New Haven"|other_city == "Newark"|other_city =="Orange"|other_city == "Powell"|other_city == "Santa Barbara"|other_city == "Yonkers"|other_city == "."
egen person_id_raw = group(city last_name first_name middle_names)
replace other_city = strtrim(other_city)
replace other_city = "zz" if other_city ==""
sort city last_name first_name middle_names other_city
local tol_line= _N
forvalues i = 1(1)`tol_line' {
    if ( `i' > 1 & person_id_raw[`i'] == person_id_raw[`i'-1] & other_city[`i'] == "zz"){
replace other_city = other_city[`i'-1] in `i' if _n > 1
	}
}
drop household_id
replace other_city = ""  if other_city == "zz"
save "SR individual main.dta", replace

drop if other_city == ""
save "SR individual temp.dta", replace

use "SR individual main.dta", clear
replace other_city = city 

append using "SR individual temp.dta"
sort last_name first_name middle_names year city
egen person_id = group(other_city last_name first_name middle_names)

bys person_id: gen count = _N
bys person_id_raw: egen mincount = min(count)
bys person_id_raw: egen minid = min(person_id)
bys person_id_raw person_id: gen id_order = _n
replace id_order = . if id_order != 1
bys person_id_raw: egen id_dupl = count(id_order)
bys person_id_raw count: gen count_order = _n
replace count_order = . if count_order != 1
bys person_id_raw: egen count_dupl = count(count_order) 

drop if mincount == count & count_dupl > 1 
drop if minid == person_id & id_dupl > 1 & count_dupl == 1
drop person_id_raw count mincount minid id_order id_dupl count_order count_dupl 

sort last_name first_name middle_names year city
egen person_id_new = group(other_city last_name first_name middle_names)
drop person_id
rename  person_id_new person_id
drop other_city

***unify personal characteristic
foreach var of varlist female college grad_year {
    bysort person_id: egen mode_`var' = mode(`var')
    replace `var' = mode_`var'
    drop mode_`var'
}
bysort person_id: egen min_married = min(year) if married == 1
bysort person_id: egen min_survived = min(year) if survived == 0
replace married = 1 if year >= min_married & person_id == person_id[_n-1]
replace survived = 1 if year >= min_survived & person_id == person_id[_n-1]
drop min_married min_survived

*foreach var of varlist last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name {
*		replace `var' = "" if `var' == "None"
*}
foreach var of varlist last_name first_name middle_names {
		replace `var' = "" if `var' == "None"
}

***reshape the dataset
sort person_id year city
bys person_id year: gen group_id = _n
*reshape wide city household_structure title spouse_name spouse_middle_names spouse_last_name clubs_abbr clubs_extended college grad_year address address_original citytown_correct county_correct state_correct region_correct female widow married survived just_married foreign foreign_original original_title, i(person_id year) j(group_id)
reshape wide city household_structure title clubs_abbr clubs_extended college grad_year address address_original citytown_correct county_correct state_correct region_correct female widow married survived just_married foreign foreign_original original_title, i(person_id year) j(group_id)
drop group_id

*save "Social Registers v3 individual.dta", replace
save "Social Registers v3 standardized individual.dta", replace

browse if last_name == "Boone" & first_name == "Charles" & middle_names == "L"