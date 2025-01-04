* Author: Valentina D'Anna (vdanna@redphd.it)
* Date: May, 2023
* Last update: May 8, 2023

/* The following code performs a fuzzy match among Social Register and IPUMS census of the same year */
clear all
set maxvar 32000
set more off
ssc install freqindex


/* Specify directory locations: */

global registers	 "~/Dropbox/registers/data/build/registers"		  	// Location where raw data for registers is held

global census	     "~/Dropbox/registers/data/build/census"  			// Location where the raw data for full count census is held



**************************
* SECTION 1. Fuzzy match *
**************************

/* 2.1 Set up for fuzzy match */

use "$census/NY_1900_census_standardized.dta", clear
gen name= f_name_cleaned + " " + m_name_initial + " " + l_name_cleaned   // Create a unique string to match
gen id_c=_n 															 // Create an id 
save "$census/NY_1900_census_standardized_fuzzy.dta", replace
  
use "$registers/Social Registers v2 inferred gender standardized.dta", clear
keep if (city=="New York" & year_reg==1900)                                             
gen name= f_name_cleaned + " " + m_name_initial + " " + l_name_cleaned   // Create a unique string to match
gen id_r=_n																 // Create an id 


/* 2.2 Fuzzy match */

matchit id_r name using "$census/NY_1900_census_standardized_fuzzy.dta", idu(id_c) txtu(name) override



