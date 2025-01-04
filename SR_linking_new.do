*******************************
***** Author: Tianrui Lai ***** 
****** Date: OCt, 2023 ********
*******************************

/* The following code conduct a year-to-year match of the individuals in the social registers. 
Step 1 performs the 1:1 match using first name and last name;
Step 2 performs the 1:m, m:1 and m:m match sequencially increasing restrictios;
Step 3 performs the 0:m and m:0 match using the NYSIIS standardized name for fuzzy match, as well as using the initial of first names, last name and additional information;
Step 4 cleans and combine the dataset.
 */

** Specify directory locations
global dta_output "C:/Users/87208/Documents/Documents/RA/Social register/dta_output"		

global matched_output  "C:/Users/87208/Documents/Documents/RA/Social register/dta_output/matched_output"

**open the log files
cd "$matched_output"
capture log close
log using SR_linking.log, replace

** Some cleaning on the variables
cd "$dta_output"
use "Social Registers_long_v3.dta", clear
gen id = _n
gen id_origin = id
keep if city == "New York"
recast str30 last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name suffix spouse_lastsurname college1 address, force
foreach var of varlist last_name first_name middle_names spouse_name spouse_middle_names spouse_last_name suffix spouse_lastsurname spouse_suffix last_surname{
		replace `var' = "" if `var' == "None"
}
abeclean first_name last_name, generate(first_c last_c first_n last_n)
abeclean spouse_name spouse_last_name, generate(spouse_c spouse_last_c spouse_n spouse_last_n) // Generate the NYSIIS standrdized name
gen middle_initial = regexs(1) if regexm(middle_names, "(^[A-Za-z])")
gen first_initial = regexs(1) if regexm(first_name, "(^[A-Za-z])")
levelsof year, local(years)
save "Social Registers_long_NY_v3.dta", replace

** Split the dataset by years
levelsof year, local(years)
local n : word count `years'
foreach year in `years'{
	use "$dta_output/Social Registers_long_NY_v3.dta", clear
    keep if (city == "New York" & year == `year') 
	local var = "id_" + "`year'"
	rename id `var'
    save "$matched_output/Social Registers_NY_`year'.dta", replace
}

**Set up the loop
use "$dta_output/Social Registers_long_NY_v3.dta", clear
levelsof year, local(years)
local n : word count `years'
forvalues i = 1/`n' {
if `i' != 60 {
	local year1 : word `i' of `years'
    local next_i = `i' + 1
	local year2 : word `next_i' of `years'
**********************************************************************
********Step 1: 1:1 match using first name and last name**************
**********************************************************************
cd "$matched_output"

use "Social Registers_NY_`year1'.dta", clear
bys last_name first_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name)      
capture keep if (dup_mas == 0 & miss_mas == 0)	  // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name using "Social Registers_NY_`year2'.dta", keepusing(id_`year2') keep(master matched)  // Merge according to last and first name

bys last_name first_name:  gen dup_use = cond(_N==1,0,_n)
egen miss_use = rowmiss(last_name first_name)  
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0)      // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_use dup_mas miss_mas miss_use
gen match_`year1'="."
replace match_`year1'="S"

save "Social Registers_NY_`year1'_matched.dta" , replace

**********************************************************************
*****************Step 2: 1:m, m:1 and m:m match **********************
*********************************************************************
/*2.1 Match individuals according to first name, last name, and spouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M1"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.2 Match individuals according to first name, last name, and spouse first name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M2"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.3 Match individuals according to first name, last name, and suffix*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name suffix)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name suffix using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name suffix: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M3"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.4 Match individuals according to first name, last name, and initial of middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_initial)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_initial using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name middle_initial: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M4"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.5 Match individuals according to first name, last name, and middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_names)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_names using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name middle_names: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M5"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.6 Match individuals according to first name, last name, and college*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name college1)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name college1 using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name college1: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M6"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.7 Match individuals according to first name, last name, and address*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name address)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name address using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name address: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M7"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.8 Match individuals according to first name, last name, and first and last name of the spouse*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M8"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.9 Match individuals according to first name, last name, spouse last name, and suffix*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name suffix spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name suffix spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name suffix spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M9"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.10 Match individuals according to first name, last name, spouse last name, and initial of the middle name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_initial spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_initial spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name middle_initial spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M10"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.11 Match individuals according to first name, last name, spouse last name, and middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_names spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_names spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name middle_names spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M11"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace 

/*2.12 Match individuals according to first name, last name, spouse last name, and college*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1 spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name college1 spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name college1 spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name college1 spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1 spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M12"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.13 Match individuals according to first name, last name, spouse last name, and address*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address spouse_last_name: gen dup_mas = cond(_N==1,0,_n)
egen miss_mas = rowmiss(last_name first_name address spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name address spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name address spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address spouse_last_name)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M13"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.14 Match individuals according to first name, last name, first and last name of the spouse, and suffix*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name suffix: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name suffix)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name suffix using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name suffix : gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name suffix)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M14"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.15 Match individuals according to first name, last name, first and last name of the spouse, and initial of the middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name middle_initial: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name middle_initial)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name middle_initial using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name middle_initial : gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name middle_initial)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M15"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.16 Match individuals according to first name, last name, first and last name of the spouse, and middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name middle_names: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name middle_names)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name middle_names using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name middle_names: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name middle_names)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M16"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.17 Match individuals according to first name, last name, first and last name of the spouse, and college*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name college1: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name college1)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name college1 using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name college1: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name college1)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M17"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*2.18 Match individuals according to first name, last name, first and last name of the spouse, and address*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name address: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name address)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name address using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name address: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name address)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="M18"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

**********************************************************************
********************Step 3: m:0 and 0:m match*************************
**********************************************************************
/*3.1 Match individuals according to first name, last name, and NYSIIS spouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data

use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N1"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.2 Match individuals according to first name, last name, and NYSIIS spouse first name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_name first_name spouse_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N2"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.3 Match individuals according to first name, last name, NYSIIS spouse first name and NYSIIS apouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_name first_name spouse_last_n spouse_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_last_n spouse_n)  
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_last_n spouse_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_last_n spouse_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_n spouse_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N3"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.4 Match individuals according to first name, last name, NYSIIS spouse last name, and suffix*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name suffix spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name suffix spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name suffix spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N4"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.5 Match individuals according to first name, last name, NYSIIS spouse last name, and initial of the middle name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_initial spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name middle_initial spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name middle_initial spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N5"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.6 Match individuals according to first name, last name, NYSIIS spouse last name, and middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_names spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name middle_names spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name middle_names spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N6"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.7 Match individuals according to first name, last name, NYSIIS spouse last name, and college*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1 spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name college1 spouse_last_n)    
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name college1 spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name college1 spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1 spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N7"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.8 Match individuals according to first name, last name, NYSIIS spouse last name, and address*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name address spouse_last_n)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name address spouse_last_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name address spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N8"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.9 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and suffix*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n suffix: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n suffix)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n suffix using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n suffix:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n suffix) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N9"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.10 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and initial of the middle name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n middle_initial: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n middle_initial)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n middle_initial using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n middle_initial:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n middle_initial) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N10"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.11 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and middle names*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n middle_names: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n middle_names)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n middle_names using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n middle_names:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n middle_names) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N11"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.12 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and college*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n college1: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n college1)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n college1 using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n college1:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n college1) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N12"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.13 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and address*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n address: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n address)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n address using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n address:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n address) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N13"

append using "Social Registers_NY_`year1'_matched.dta"             
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.14 Match individuals according to NYSIIS first name, last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data
 
bys last_name first_n spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_n spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_n spouse_name spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_n spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_n spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N14"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.15 Match individuals according to first name, NYSIIS last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_name spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_name spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_name spouse_name spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_n first_name spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_name spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N15"

append using "Social Registers_NY_`year1'_matched.dta"               
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.16 Match individuals according to NYSIIS first name, NYSIIS last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_n spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_n spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_n spouse_name spouse_last_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_n first_n spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_n spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N16"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace                      

/*3.17 Match individuals according to first name and NYSIIS last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_name using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_n first_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N17"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.18 Match individuals according to NYSIIS first name and last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_name first_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_n) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_name first_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N18"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace

/*3.19 Match individuals according to NYSIIS first name and NYSIIS last name*/
use "Social Registers_NY_`year2'.dta", clear       
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2') keep(master) nogenerate  
save "Social Registers_NY_`year2'_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_n) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_n using "Social Registers_NY_`year2'_unmatched.dta", keepusing(id_`year2') keep(master matched)  // Merge according to all information
bys last_n first_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1' = "."
replace match_`year1'="N19"

append using "Social Registers_NY_`year1'_matched.dta"   
save "Social Registers_NY_`year1'_matched.dta", replace

**********************************************************************
*******************Step 4: Assign individual id***********************
**********************************************************************
use "Social Registers_NY_`year1'.dta", clear 
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year2' match_`year1') nogenerate
rename match_`year1' match_as_master
rename id_`year1' id_new
rename id_`year2' id_matched_using

replace match_as_master = "null" if match_as_master == ""
bys year match_as_master: egen count_type = count(match_as_master) // Count the number of matching cases as the master dataset for each type
save "Social Registers_NY_`year1'.dta", replace

use "Social Registers_NY_`year2'.dta", clear 
merge 1:1 id_`year2' using "Social Registers_NY_`year1'_matched.dta", keepusing(id_`year1' match_`year1') 
replace id_`year2' = id_`year1' if _merge == 3
rename match_`year1' match_as_using
replace match_as_using = "null" if match_as_using == ""
drop _merge id_`year1'
save "Social Registers_NY_`year2'.dta", replace
	}
}
log close

**********************************************************************
***********Step 5: Break the panel for different people***************
**********************************************************************

***Revise the variable name of last dataset 
cd "$matched_output"
local dtafiles: dir . files"*.dta"
use "Social Registers_NY_1958.dta", clear
rename id_1958 id_new
save "Social Registers_NY_1958.dta", replace
drop if year > 0
save "$dta_output/Social Registers_long_matched_NY_v3.dta", replace

use "$dta_output/Social Registers_long_NY_v3.dta", clear
levelsof year, local(years)
local n : word count `years'
forvalues i = 1/`n' {
if `i' != 60 {
	local year1 : word `i' of `years'
    local next_i = `i' + 1
	local year2 : word `next_i' of `years'

cd "$matched_output"
use "Social Registers_NY_`year2'.dta", clear 
rename college1 college1_y
rename middle_names middle_names_y
rename id_origin id_origin_y
save, replace

use "Social Registers_NY_`year1'.dta", clear 
merge 1:1 id_new using "Social Registers_NY_`year2'.dta", keepusing(id_origin_y college1_y middle_names_y) keep(match) nogenerate // Sort out all the matched people in the previous procedure
save "Social Registers_NY_`year1'_notexactmatched.dta", replace

use "Social Registers_NY_`year2'.dta", clear 
rename college1_y college1
rename middle_names_y middle_names
rename id_origin_y id_origin
save, replace

use "Social Registers_NY_`year1'_notexactmatched.dta", clear 
merge 1:1 id_new college1 middle_names using "Social Registers_NY_`year2'.dta", keepusing(id_new) // Sort out the exactly matched people with college, graduation year or full middle names
drop if _merge == 3 | college1 == "" | middle_names == "" | regexm(middle_names, "^[^a-z]*$") | college1_y == "" | middle_names_y == "" | regexm(middle_names_y, "^[^a-z]*$") // Keep only the people with different college and graduation year, or full middle names
gen id_replace = id_origin_y
save "Social Registers_NY_`year1'_notexactmatched.dta", replace

forvalues j = 1/`n' {
	if `j' > `i' {
		local year_after : word `j' of `years'
		use "Social Registers_NY_`year_after'.dta", clear
		drop if city == ""
		merge 1:1 id_new using "Social Registers_NY_`year1'_notexactmatched.dta", keepusing(id_replace)
		replace id_new = id_replace if _merge == 3
		egen split_`year1' = total(_merge == 3)
		drop if _merge == 2
		drop _merge id_replace
		save "Social Registers_NY_`year_after'.dta", replace
		}
	}
}
}

**********************************************************************
*********Step 6: Concatenate the panel for the same people************
**********************************************************************
use "$dta_output/Social Registers_long_NY_v3.dta", clear
levelsof year, local(years)
local n : word count `years'
forvalues i = 1/`n' {
if `i' != 60 {
	local year1 : word `i' of `years'
    local next_i = `i' + 2
	local year3 : word `next_i' of `years'

cd "$matched_output"

use "Social Registers_NY_`year1'.dta", clear 
rename id_new id_`year1'
keep if match_as_master == "null"
save "Social Registers_NY_`year1'_forconcat.dta", replace
use "Social Registers_NY_`year3'.dta", clear 
rename id_new id_`year3'
keep if match_as_using == "null"
save "Social Registers_NY_`year3'_forconcat.dta", replace

/*6.1.1 Match individuals according to first name and last name*/
use "Social Registers_NY_`year1'_forconcat.dta", clear
bys last_name first_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name)      
capture keep if (dup_mas == 0 & miss_mas == 0)	  // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name using "Social Registers_NY_`year3'_forconcat.dta", keepusing(id_`year3') keep(master matched)  // Merge according to last and first name

bys last_name first_name:  gen dup_use = cond(_N==1,0,_n)
egen miss_use = rowmiss(last_name first_name)  
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0)      // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_use dup_mas miss_mas miss_use
gen match_`year1'_concat="."
replace match_`year1'_concat="S"

save "Social Registers_NY_`year1'_forconcat_matched.dta" , replace

/*6.2.1 Match individuals according to first name, last name, and spouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M1"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.2 Match individuals according to first name, last name, and spouse first name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M2"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.3 Match individuals according to first name, last name, and suffix*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name suffix)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name suffix using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name suffix: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M3"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.4 Match individuals according to first name, last name, and initial of middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_initial)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_initial using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name middle_initial: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M4"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.5 Match individuals according to first name, last name, and middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_names)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_names using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name middle_names: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M5"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.6 Match individuals according to first name, last name, and college*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name college1)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name college1 using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name college1: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M6"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.7 Match individuals according to first name, last name, and address*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name address)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name address using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name address: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M7"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.8 Match individuals according to first name, last name, and first and last name of the spouse*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name)      
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M8"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.9 Match individuals according to first name, last name, spouse last name, and suffix*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name suffix spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name suffix spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name suffix spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M9"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.10 Match individuals according to first name, last name, spouse last name, and initial of the middle name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_initial spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_initial spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name middle_initial spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M10"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.11 Match individuals according to first name, last name, spouse last name, and middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name middle_names spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name middle_names spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name middle_names spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M11"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace 

/*6.2.12 Match individuals according to first name, last name, spouse last name, and college*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1 spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name college1 spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name college1 spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name college1 spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1 spouse_last_name)   
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M12"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.13 Match individuals according to first name, last name, spouse last name, and address*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address spouse_last_name: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name address spouse_last_name)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name address spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name address spouse_last_name: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address spouse_last_name)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M13"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.14 Match individuals according to first name, last name, first and last name of the spouse, and suffix*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name suffix: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name suffix)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name suffix using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name suffix : gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name suffix)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M14"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.15 Match individuals according to first name, last name, first and last name of the spouse, and initial of the middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name middle_initial: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name middle_initial)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name middle_initial using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name middle_initial : gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name middle_initial)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M15"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.16 Match individuals according to first name, last name, first and last name of the spouse, and middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name middle_names: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name middle_names)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name middle_names using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name middle_names: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name middle_names)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M16"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.17 Match individuals according to first name, last name, first and last name of the spouse, and college*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name college1: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name college1)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name college1 using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name college1: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name college1)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M17"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.2.18 Match individuals according to first name, last name, first and last name of the spouse, and address*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_name spouse_last_name address: gen dup_mas = cond(_N==1,0,_n)  
egen miss_mas = rowmiss(last_name first_name spouse_name spouse_last_name address)      
capture keep if (dup_mas == 0 & miss_mas == 0) // Keep only uniquely identified observations with non-missing value with non-missing value

merge 1:m last_name first_name spouse_name spouse_last_name address using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information

bys last_name first_name spouse_name spouse_last_name address: gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_name spouse_last_name address)  

capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="M18"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.1 Match individuals according to first name, last name, and NYSIIS spouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data

use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N1"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.2 Match individuals according to first name, last name, and NYSIIS spouse first name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_name first_name spouse_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N2"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.3 Match individuals according to first name, last name, NYSIIS spouse first name and NYSIIS apouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_name first_name spouse_last_n spouse_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_last_n spouse_n)  
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_last_n spouse_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_last_n spouse_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_last_n spouse_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N3"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.4 Match individuals according to first name, last name, NYSIIS spouse last name, and suffix*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name suffix spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name suffix spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name suffix spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name suffix spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name suffix spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N4"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.5 Match individuals according to first name, last name, NYSIIS spouse last name, and initial of the middle name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_initial spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_initial spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name middle_initial spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name middle_initial spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_initial spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N5"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.6 Match individuals according to first name, last name, NYSIIS spouse last name, and middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name middle_names spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name middle_names spouse_last_n)      
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name middle_names spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name middle_names spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name middle_names spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N6"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.7 Match individuals according to first name, last name, NYSIIS spouse last name, and college*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name college1 spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name college1 spouse_last_n)    
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name college1 spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name college1 spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name college1 spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N7"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.8 Match individuals according to first name, last name, NYSIIS spouse last name, and address*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name address spouse_last_n: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name address spouse_last_n)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name address spouse_last_n using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name address spouse_last_n:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name address spouse_last_n) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N8"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.9 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and suffix*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n suffix: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n suffix)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n suffix using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n suffix:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n suffix) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N9"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.10 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and initial of the middle name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n middle_initial: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n middle_initial)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n middle_initial using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n middle_initial:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n middle_initial) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N10"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.11 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and middle names*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n middle_names: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n middle_names)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n middle_names using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n middle_names:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n middle_names) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N11"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.12 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and college*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n college1: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n college1)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n college1 using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n college1:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n college1) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N12"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.13 Match individuals according to first name, last name, NYSIIS first and last name of the spouse, and address*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data

bys last_name first_name spouse_n spouse_last_n address: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_name spouse_n spouse_last_n address)     
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_name spouse_n spouse_last_n address using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_name spouse_n spouse_last_n address:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_name spouse_n spouse_last_n address) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N13"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"             
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.14 Match individuals according to NYSIIS first name, last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data
 
bys last_name first_n spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_name first_n spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_name first_n spouse_name spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_name first_n spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_name first_n spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N14"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.15 Match individuals according to first name, NYSIIS last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_name spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_name spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_name spouse_name spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_n first_name spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_name spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N15"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"               
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.3.16 Match individuals according to NYSIIS first name, NYSIIS last name, spouse first name and spouse last name*/
use "Social Registers_NY_`year3'_forconcat.dta", clear       
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3') keep(master) nogenerate  
save "Social Registers_NY_`year3'_forconcat_unmatched.dta", replace // Remove the matched individuals from using data
use "Social Registers_NY_`year1'_forconcat.dta", clear       
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1') keep(master) nogenerate  // Remove the matched individuals from master data 

bys last_n first_n spouse_name spouse_last_name: gen dup_mas = cond(_N==1,0,_n) 
egen miss_mas = rowmiss(last_n first_n spouse_name spouse_last_name) 
capture keep if (dup_mas == 0 & miss_mas == 0)  // Keep only uniquely identified observations with non-missing value
merge 1:m last_n first_n spouse_name spouse_last_name using "Social Registers_NY_`year3'_forconcat_unmatched.dta", keepusing(id_`year3') keep(master matched)  // Merge according to all information
bys last_n first_n spouse_name spouse_last_name:  gen dup_use = cond(_N==1,0,_n) 
egen miss_use = rowmiss(last_n first_n spouse_name spouse_last_name) 
capture keep if (dup_use == 0 & _merge==3 & miss_use == 0) // Keep only 1:1 merge uniquely identified with non-missing value
capture drop _merge dup_mas dup_use miss_mas miss_use
gen match_`year1'_concat = "."
replace match_`year1'_concat="N16"

append using "Social Registers_NY_`year1'_forconcat_matched.dta"   
save "Social Registers_NY_`year1'_forconcat_matched.dta", replace

/*6.4.1 Assign the same individual ids to matched people in the two dataset*/
use "Social Registers_NY_`year1'.dta", clear 
rename id_new id_`year1'
merge 1:1 id_`year1' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year3' match_`year1'_concat) nogenerate
rename match_`year1'_concat match_as_master_concat
rename id_`year1' id_new
rename id_`year3' id_matched_using_concat

replace match_as_master_concat = "null" if match_as_master_concat == ""
bys year match_as_master_concat: egen count_type_concat = count(match_as_master) // Count the number of matching cases as the master dataset for each type
save "Social Registers_NY_`year1'.dta", replace

use "Social Registers_NY_`year3'", clear 
rename id_new id_`year3'
merge 1:1 id_`year3' using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1' match_`year1'_concat) 
replace id_`year3' = id_`year1' if _merge == 3
rename match_`year1'_concat match_as_using_concat
replace match_as_using_concat = "null" if match_as_using_concat == ""
drop _merge id_`year1'
save "Social Registers_NY_`year3'.dta", replace

/*6.4.2 Assign the same individual ids to matched people in all following dataset*/
forvalues j = 1/`n' {
if `j' > `year3' {
	local year_after : word `j' of `years'
	use "Social Registers_NY_`year_after'.dta", clear
	merge 1:1 id_original using "Social Registers_NY_`year1'_forconcat_matched.dta", keepusing(id_`year1')
	replace id_new = id_`year1' if _merge == 3
	replace match_as_using_concat = "link" if (match_as_using_concat == "null" & _merge == 3)
	drop if _merge == 2
	drop id_`year1' _merge
	save "Social Registers_NY_`year_after'.dta", replace
		}
	}
}
}

**********************************************************************
*******************Step 7: Generate final dataset*********************
**********************************************************************
cd "$matched_output"
local dtafiles: dir . files"*.dta"
use "$dta_output/Social Registers_long_matched_NY_v3.dta", clear
foreach file of local dtafiles{
	if regexm("`file'", "unmatched", "forconcat", "notexactmatched") == 0 & "`file'" != "Social Registers_NY_`year1'_matched.dta" { // The name is read as lower case letter
	display "`file'"
	use "`file'", clear
	append using "$dta_output/Social Registers_long_matched_NY_v3.dta"
	save "$dta_output/Social Registers_long_matched_NY_v3.dta", replace
	}
} 

drop first_c last_c first_n last_n
save "$dta_output/Social Registers_long_matched_NY_v3.dta", replace

collapse (mean) split*
keep split*
export excel using "summary.xlsx", firstrow(variables) replace


*********************Summary of matching**********************
bys year: egen total_count = count(year)
bys year match_as_master_concat: egen count_type_concat = count(year)
bys year match_as_using_concat: egen count_type_concat2 = count(year)
gen percent = (count_type / total_count) * 100
gen percent_concat = (count_type_concat / total_count) * 100
gen percent_concat2 = (count_type_concat2 / total_count) * 100

* Collapse the dataset
collapse (mean) total_count count_type count_type_concat count_type_concat2 percent percent_concat percent_concat2, by(year match_as_master match_as_master_concat match_as_using_concat)

* Calculate the average 
replace count_type = . if year == 1958
replace percent = . if year == 1958
replace count_type_concat = . if year == 1958
replace percent_concat = . if year == 1958
replace count_type_concat2 = . if year == 1899
replace percent_concat2 = . if year == 1899
egen avg_count_type = mean(count_type), by(match_as_master)
egen avg_percent = mean(percent), by(match_as_master)
egen avg_count_type_concat = mean(count_type_concat), by (match_as_master_concat)
egen avg_count_type_concat2 = mean(count_type_concat2), by (match_as_using_concat)


export excel using "summary.xlsx", firstrow(variables) replace

log close

xtset id_new year
xtdescribe, patterns(1000)

