* Author: Valentina D'Anna (vdanna@redphd.it)
* Date: April, 2023
* Last update: June 27, 2023

/* The following code is used to infer gender of Social Register individuals using the ±5 years interval around the census year. We assign to each individual a probability of being female given the probability that such name appears in the census and it corresponds to a woman. */

clear all
set maxvar 32000
set more off


/* Specify directory locations: */
global MatchingDoFiles   "~/Dropbox/registers/code_census/build/abe_algorithm_code/codes"  	   // Location where all ABE/Ferrie matching algorithm files (and .ado files) are stored

global census	     "~/Dropbox/registers/data/build/census"  			// Location where the raw data for full count census is held

global registers	 "~/Dropbox/registers/data/build/registers"		    // Location where raw data for registers is held

global ipums         "~\Dropbox\IPUMS"                                  // Location where IPUMS data for census is held

global temporary     "~\Dropbox\register_trial"                         // Location where temporary files are located



* Collapse from cansus with non standardized names *
cd "C:/Users/87208/Documents/Documents/RA/Social register/dta_output"

use "$ipums/names/names1900.dta" 
gen f_name=lower(namefrst)
recode sex (1=0)(2=1), gen(female)
collapse female, by(f_name)             // Probability of being female given a specific name

gen sex=1
replace sex=2 if female>0.5             // Assign gender given the probability of being female
label variable sex "sex"
label define SEX 1 "male"  2 "female", replace
label values sex SEX

save "$temporary/collapse_non_standardized.dta", replace


* Attach gender to Social Register *

use "$registers/Social Registers v3.dta", clear
keep if (year==1895 | year==1896 | year==1897 | year==1898 | year==1899 | year==1900 | year==1901 | year==1902 | year==1903 | year==1904)   // Restrict to ±5 years interval with respect to the census
gen f_name=lower(first_name)
rename female female_old                // Comparison with old female dummy (given by the title)

merge m:1 f_name using "~/Dropbox/register_trial/collapse_non_standardized.dta",keep(master match) keepusing(female sex)            // Merge gender from IPUMS by f_name to social register f_name
drop _merge

save "$registers/Social Registers v3 inferred gender.dta", replace







