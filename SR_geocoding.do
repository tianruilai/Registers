cd "C:\Users\87208\Documents\Documents\RA\Social register\dta_output"
use "Social Registers v3.dta", clear

replace county_correct = "Albany" if citytown_correct == "Albany"
replace citytown_correct = "" if citytown_correct == "Albany"
replace county_correct = "Kings" if region_correct == "Brooklyn"
replace county_correct = "Richmond" if region_correct == "Staten Island"
replace county_correct = "Suffolk" if region_correct == "Long Island"

keep if city == "New York"
drop city
keep year first_name middle_names last_name citytown_correct state_correct county_correct
rename first_name first
rename last_name surname
rename middle_names middle
rename state_correct state
rename county_correct county
rename citytown_correct city

replace city = city + " city" if city != ""
replace county = county + " County" if county != ""
replace state = "New York" if state ==  ""

rename state state_full
merge m:1 state_full using "StateFIPS.dta", keepusing(abbr)
drop if _merge == 2
drop _merge
merge m:1 county state using "CountyFIPS.dta" 
drop if _merge == 2
drop _merge
rename city place
merge m:1 place state using "PlaceFIPS.dta", keepusing(countyfips) update
drop if _merge == 2
drop _merge
merge m:1 state using "StateFIPS.dta", keepusing(countyfips) update
drop if _merge == 2
drop _merge

save "NY names.dta", replace
