* Author: Valentina D'Anna (vdanna@redphd.it)
* Date: July, 2023
* Last update: July 16, 2023

/* The following code merges individuals in the Social Register with individuals in the census of the same year using increasing geographic progressivity and using restriction on the first name, last name, middle name initial and first name of the sposue in descending order (from more to less restrictive).

Section 1 uses the cleaned (standardized) names criterion and Section 2 uses the NYSIIS pronunciation criterion.
We prioritize matched observation from standardized names over the NYSIIS.

In Section 3 we clean the two final datasets from duplicates of histid.

In Section 4 we construct the final dataset merging the obsarvations obtained with both standardized and NYSIIS criteria. */


clear all
set maxvar 32000
set more off


/* Specify directory locations: */

global registers	     "~/Dropbox/registers/data/build/registers"		    				  // Location where raw data for registers is held

global census			 "~/Dropbox/registers/data/build/census"  							  // Location where the raw data for full count census is held

global matchdir 		 "~/Dropbox/registers/data/build/matched"			   				  // Location to store matched data



**********************************************************************************************************************
* SECTION 1. Merge register and census 1900 according to standardized name from more restrictive to less restrictive *
**********************************************************************************************************************


/*1.1.1 Merge individuals in other states according to first name, last name, middle name initial and, first name of the spouse */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)                                                //Register restriction
drop if (stateicp==13 | stateicp==99)                                                      //No New York

bys stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned :  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											           // Keep only uniquely identified observations


merge 1:m stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned  using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned


bys stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned :  gen dup_merge = cond(_N==1,0,_n)  				// Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST1"

save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace                            // Store results for 1:1 matched



/*1.1.2 Merge individuals in other states according to first name, last name and, first name of the spouse  */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)          // Look at uniquely identified observations 
keep if dup_reg<1            											                                  // Keep only uniquely identified observations


merge 1:m stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last name cleaned, first name cleaned and middle name initial

bys stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  	   // Look at not uniquely identified observations after merge
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST2"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                          // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 



/*1.1.3 Merge individuals in other states according to first name, last name and, middle name initial */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_cleaned f_name_cleaned m_name_initial:  gen dup_reg = cond(_N==1,0,_n)          // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_cleaned f_name_cleaned m_name_initial using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last name cleaned, first name cleaned and middle name initial

bys stateicp l_name_cleaned f_name_cleaned m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  	   // Look at not uniquely identified observations after merge
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST3"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 



/*1.1.4 Merge individuals in other states according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_cleaned f_name_cleaned: gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_cleaned f_name_cleaned using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned


bys stateicp l_name_cleaned f_name_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST4"

append using $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 




/*1.2.1 Merge individuals in New York city according to first name, last name, middle name initial and, first name of the spouse */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99)
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals  


bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC1"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace



/*1.2.2 Merge individuals in New York city according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99)
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals  


bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned f_name_spouse_cleaned using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC2"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace


/*1.2.3 Merge individuals in New York city according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99)
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals  


bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC3"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace



/*1.2.4 Merge individuals in New York city according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC4"

append using $matchdir//Final//Reverse//New_York_1900_stand.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace   



/*1.3.1 Merge individuals in New York SEA according to first name, last name, middle name initial and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA1"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 

/*1.3.2 Merge individuals in New York SEA according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned f_name_spouse_cleaned using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA2"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 


/*1.3.3 Merge individuals in New York SEA according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA3"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                       // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 



/*1.3.4 Merge individuals in New York SEA according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA4"

append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace  


/*1.4.1 Merge individuals in New York State according to first name, last name, middle name initial and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations a
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS1"


append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 

/*1.4.2 Merge individuals in New York State according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned f_name_spouse_cleaned using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned f_name_spouse_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS2"


append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 


/*1.4.3 Merge individuals in New York State according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned m_name_initial using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS3"


append using  $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace 



/*1.4.4 Merge individuals in New York State according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_stand.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_cleaned f_name_cleaned:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_cleaned f_name_cleaned using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_cleaned f_name_cleaned:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS4"


append using $matchdir//Final//Reverse//New_York_1900_stand.dta                                        // Store results for 1:1 matched
gen technique="."
replace technique="STAND"
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_stand.dta , replace   



************************************************************************************
* SECTION 2. Merge register and census 1900 according to NYSIIS name pronunciation *
************************************************************************************

/*2.1.4 Merge individuals in other states according to first name, last name, middle name initial and, first name of the spouse */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)                                                //Register restriction
drop if (stateicp==13 | stateicp==99)                                                    //No New York

bys stateicp l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned


bys stateicp l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST1"

save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace 



/*2.1.2 Merge individuals in other states according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)          // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_nysiis f_name_nysiis f_name_spouse_nysiis using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last name cleaned, first name cleaned and middle name initial

bys stateicp l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  	   // Look at not uniquely identified observations after merge
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST2"


append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                          // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta  , replace 



/*2.1.3 Merge individuals in other states according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_nysiis f_name_nysiis m_name_initial:  gen dup_reg = cond(_N==1,0,_n)          // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_nysiis f_name_nysiis m_name_initial using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last name cleaned, first name cleaned and middle name initial

bys stateicp l_name_nysiis f_name_nysiis m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  	   // Look at not uniquely identified observations after merge
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST3"


append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta   , replace 


/*2.1.4 Merge individuals in other states according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
drop if (stateicp==13 | stateicp==99)                              //No New York                                                                
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys stateicp l_name_nysiis f_name_nysiis :  gen dup_reg = cond(_N==1,0,_n)          // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m stateicp l_name_nysiis f_name_nysiis using "$census/Other_States_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last name cleaned, first name cleaned and middle name initial

bys stateicp l_name_nysiis f_name_nysiis :  gen dup_merge = cond(_N==1,0,_n)  	   // Look at not uniquely identified observations after merge
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="OST4"


append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta   , replace 


/*2.2.1 Merge individuals in New York city according to first name, last name, middle name initial and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC1"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  

/*2.2.2 Merge individuals in New York city according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis f_name_spouse_nysiis using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC2"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  

/*2.2.3 Merge individuals in New York city according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC3"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  

/*2.2.4 Merge individuals in New York city according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis using "$census/New_York_city_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYC4"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  


/*2.3.1 Merge individuals in New York SEA according to first name, last name, middle name initial and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA1"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                          // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta  , replace  


/*2.3.2 Merge individuals in New York SEA according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis f_name_spouse_nysiis using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA2"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta  , replace


/*2.3.3 Merge individuals in New York SEA according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA3"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta  , replace  


/*2.3.4 Merge individuals in New York SEA according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta , keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis using "$census/New_York_SEA_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="SEA4"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                          // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta  , replace 


/*2.4.1 Merge individuals in New York State according to first name, last name, middle name initial and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS1"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                        // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  

/*2.4.2 Merge individuals in New York State according to first name, last name and, first name of the spouse*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis f_name_spouse_nysiis using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis f_name_spouse_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS2"

append using  $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned f_name_spouse_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace


/*2.4.3 Merge individuals in New York State according to first name, last name and, middle name initial*/

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis m_name_initial using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis m_name_initial:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS3"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                         // Store results for 1:1 matched
sort stateicp l_name_cleaned f_name_cleaned m_name_initial
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace  


/*2.4.4 Merge individuals in New York State according to first name and last name */

use "$registers/Social Registers v3 inferred gender standardized states.dta", clear
keep if (city=="New York" & year_reg==1900)    						//Restrictions   
keep if (stateicp==13 | stateicp==99) 							 //Only New York state and not specified
merge 1:1 id using $matchdir//Final//Reverse//New_York_1900_nysiis.dta, keepusing(l_name_cleaned f_name_cleaned) keep(master) nogenerate  // Remove the already matched individuals 


bys l_name_nysiis f_name_nysiis:  gen dup_reg = cond(_N==1,0,_n)        // Look at uniquely identified observations 
keep if dup_reg<1            											                   // Keep only uniquely identified observations


merge 1:m l_name_nysiis f_name_nysiis using "$census/New_York_state_1900_census_standardized.dta", keepusing(histid bpl age relate) keep(master matched)  // Merge according to last and first name cleaned

bys l_name_nysiis f_name_nysiis:  gen dup_merge = cond(_N==1,0,_n)  					   // Look at not uniquely identified observations after merge 
keep if (dup_merge<1 & _merge==3) 									                       // Keep only 1:1 merge uniquely identified
drop _merge

gen match="."
replace match="NYS4"

append using $matchdir//Final//Reverse//New_York_1900_nysiis.dta                                        // Store results for 1:1 matched
gen technique="."
replace technique="NYSIIS"
sort stateicp l_name_cleaned f_name_cleaned
save $matchdir//Final//Reverse//New_York_1900_nysiis.dta , replace 


*******************************************************
* SECTION 3. Cleaning datasets of matched individuals *
*******************************************************

use $matchdir//Final//Reverse//New_York_1900_stand.dta  , clear
bys histid:  gen dup_histid = cond(_N==1,0,_n)     //Create variable of histid duplicates
tab dup_histid
br if dup_histid>0
br id household_id household_structure title l_name first_name m_name f_name_spouse state_correct relate age bpl histid match technique dup_histid if dup_histid>0
drop if dup_histid>0     //Drop histid duplicates
br
save $matchdir//Final//Reverse//New_York_1900_stand_temporary.dta 


use $matchdir//Final//Reverse//New_York_1900_nysiis.dta , clear
bys histid:  gen dup_histid = cond(_N==1,0,_n)    //Create variable of histid duplicates
tab dup_histid
br if dup_histid>0
br id household_id household_structure title l_name first_name m_name f_name_spouse state_correct relate age bpl histid match technique dup_histid if dup_histid>0
drop if dup_histid>0     //Drop histid duplicates
br
save $matchdir//Final//Reverse//New_York_1900_nysiis_temporary.dta 


***************************************************
* SECTION 4. Final dataset of matched individuals *
***************************************************

use $matchdir//Final//Reverse//New_York_1900_stand_temporary.dta , clear
merge 1:1 histid using $matchdir//Final//Reverse//New_York_1900_nysiis_temporary.dta, 
save $matchdir//Final//Reverse//New_York_1900_final_temporary.dta, replace














































