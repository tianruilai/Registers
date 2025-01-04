* Author: Valentina D'Anna (vdanna@redphd.it)
* Date: May, 2023
* Last update: May 26, 2023

/* The following code aims to stadardize first an last names of the individuals in the Social register using the standardization command 'abeclean' provided by Abramitzky, Boustan and Eriksson. It provides us with cleaned names, middle name initials and NYSIIS names, according to the gender of the individual. */

clear all
set maxvar 32000
set more off
ssc install nysiis


/* Specify directory locations: */

global MatchingDoFiles   "~/Dropbox/registers/code_census/build/abe_algorithm_code/codes"  	   // Location where all ABE/Ferrie matching algorithm files (and .ado files) are stored

global registers	 "~/Dropbox/registers/data/build/registers"		  		// Location where raw data for registers is held


*****************************************
* SECTION 1. Standardize and Clean Data *
*****************************************

/* 1.1 - Standardize names variables for registers data using abeclean.ado. */

use "$registers/Social Registers v3 inferred gender.dta", clear


rename year year_reg 	  	     				// Define register year
rename last_name l_name 						// Call last name "l_name"
rename middle_names m_name                      // Call middle name "m_name"
rename spouse_name f_name_spouse                // Call spouse first name "f_name_spouse"       
rename spouse_last_name l_name_spouse           // Call spouse last name "l_name_spouse"
rename spouse_middle_names m_name_spouse        // Call spouse middle name "m_name_spouse"
order title, before(l_name)

recode sex (1=2)(2=1)(else=.), gen(sex_spouse)      //Create sex_spouse variable
replace sex_spouse=. if f_name_spouse==""
label variable sex_spouse "sex of the spouse"
label define SEX_SPOUSE 1 "male"  2 "female", replace
label values sex_spouse SEX_SPOUSE


save "$registers/Social Registers v3 inferred gender standardized.dta", replace

cd $MatchingDoFiles
use "$registers/Social Registers v3 inferred gender standardized.dta", clear
gen m_name_initial=substr(m_name, 1, 1)                                       // Create middle name initial variable 
replace m_name_initial=lower(m_name_initial)
abeclean f_name l_name, nicknames sex(sex)                                    // Cleaning first and last name of head of household
gen m_name_spouse_initial=substr(m_name_spouse, 1, 1)                         // Create middle name initial variable of the spouse
replace m_name_spouse_initial=lower(m_name_spouse_initial)
abeclean f_name_spouse l_name_spouse, nicknames sex(sex_spouse)               // Cleaning first and last name of sposue

save "$registers/Social Registers v3 inferred gender standardized.dta", replace
