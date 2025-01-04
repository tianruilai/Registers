clear all
global dta_input "C:\Users\87208\Documents\Documents\RA\Social register\dta_output"
global image_path "C:\Users\87208\Documents\Documents\RA\Social Register\images"

cd"$dta_input"
use "Social Registers_long_v3.dta",clear
keep if city == "New York"

***Some results from  the table
tab year
bys year: egen num_obs = count(year)
twoway line num_obs year, sort
graph save "$image_path/Number of Observations.png", replace

preserve
bys year: egen num_hh = nvals(household_id)
duplicates drop year num_hh, force
list year num_hh 
twoway line num_hh year, sort
graph save "$image_path/Number of Households.png", replace
restore

tab year household_structure, row
bys year household_structure: gen num_structure = _N
gen prop_structure = num_structure / num_obs
twoway (line prop_structure year if household_structure == 0, lcolor(orange)) ///
       (line prop_structure year if household_structure == 1, lcolor(cyan)) ///
       (line prop_structure year if household_structure == 2, lcolor(brown)) ///
       (line prop_structure year if household_structure == 3, lcolor(red)) ///
       (line prop_structure year if household_structure == 4, lcolor(yellow)) ///
       (line prop_structure year if household_structure == 5, lcolor(magenta)) ///
       , legend(label(1 "None") label(2 "Head") label(3 "Spouse") label(4 "Junior") label(5 "Other") label(6 "OtherwithIndent")) ///
       ytitle("Proportion") xtitle("Year")
graph save "$image_path\Proportion of Family Roles.png", replace

tab year female, row
bys year: egen num_fe = sum(female == 1)
gen prop_fe = num_fe/num_obs
twoway line prop_fe year, sort
graph save "$image_path\Proportion of Females.png", replace

preserve
replace other_city =  "" if other_city == "."
tab year other_city
bys year: egen num_new = count(other_city)
gen prop_new = num_new/num_obs
duplicates drop year prop_new, force
list year prop_new
twoway line prop_new year, sort
graph save "$image_path\Proportions of Other Registers.png", replace
restore

preserve
bys year: egen num_state = count(state_correct)
gen prop_state = num_state/num_obs
duplicates drop year prop_state, force
list year prop_state
twoway line prop_state year, sort
graph save "$image_path\Proportions of Other States.png", replace
restore

preserve
bysort year: egen num_foreign = sum(foreign)
gen prop_foreign = num_foreign/num_obs
duplicates drop year prop_foreign, force
list year prop_foreign
twoway line prop_foreign year, sort
graph save "$image_path\Proportions of Other Countries.png", replace
restore

preserve
replace other_city = "New York" if city == "New York" & state_correct == ""
bys other_city: gen freq_city =_N
duplicates drop other_city, force
encode other_city, generate(register_city)
keep city register_city freq_city
reshape wide freq_city, i(city) j(register_city)
export delimited using "$image_path\Locations by register.csv", replace
restore

preserve
replace state_correct = "New York" if city == "New York" & state_correct == ""
bys state_correct: gen freq_state =_N
duplicates drop state_correct, force
encode state_correct, generate(state)
keep city state freq_state
reshape wide freq_state, i(city) j(state)
export delimited using "$image_path\Locations by address.csv", replace
restore

******College******
foreach var of varlist college1 college2 college3 {
    replace `var' = regexr(`var', "Graduate", "")
    replace `var' = regexr(`var', "[0-9]+", "")
}
foreach var of varlist college college1 college2 college3{
        replace `var' = strtrim(`var')
		replace `var' = "" if `var' == "."
}

gen decade = year - mod(year, 10)
gen id = _n
keep year id college1-college3
reshape long college, i(id) j(number) string
gen college_geo = ""
replace college_geo = "East Coast" if inlist(college, "Brown University", "City of NY College", "Columbia", "Dartmouth", "Harvard", "New York University", "Princeton", "University of Pa", "Yale")
replace college_geo = "Midwest" if inlist(college, "Amherst", "Bowdoin", "Hamilton", "Hobart", "Trinity", "Union College", "Williams")
replace college_geo = "West Coast" if inlist(college, "Cornell", "Johns Hopkins", "Rensselaer Polytechnic Institute", "Rutgers")
gen college_prestige = "" 
replace college_prestige = "Top Tier" if inlist(college, "Harvard", "Yale", "Princeton", "Columbia")
replace college_prestige = "Mid Tier" if inlist(college, "Brown University", "Cornell", "Dartmouth", "Johns Hopkins", "New York University")
replace college_prestige = "Others" if college_prestige =="" & college != ""

gen decade = floor(year/10)*10
egen count_all = total(college != ""), by(decade)
egen count_east = total(college_geo == "East Coast"), by(decade)
egen count_midwest = total(college_geo == "Midwest"), by(decade)
egen count_west = total(college_geo == "West Coast"), by(decade)
egen count_top_tier = total(college_prestige == "Top Tier"), by(decade)
egen count_mid_tier = total(college_prestige == "Mid Tier"), by(decade)
egen count_others = total(college_prestige == "Others"), by(decade)

gen prop_east = count_east / count_all
gen prop_midwest = count_midwest / count_all
gen prop_west = count_west / count_all
gen prop_top_tier = count_top_tier / count_all
gen prop_mid_tier = count_mid_tier / count_all
gen prop_others = count_others / count_all

twoway (line prop_east decade, lcolor(red)) ///
       (line prop_midwest decade, lcolor(blue)) ///
       (line prop_west decade, lcolor(green)) ///
       (scatter prop_east decade, mcolor(red)) ///
       (scatter prop_midwest decade, mcolor(blue)) ///
       (scatter prop_west decade, mcolor(green)), ///
       legend(order(1 "East Coast" 2 "Midwest" 3 "West Coast"))
graph save "$image_path\Proportion of college by region.png", replace
twoway (line prop_top_tier decade, lcolor(red)) ///
       (line prop_mid_tier decade, lcolor(blue)) ///
       (line prop_others decade, lcolor(green)) ///
       (scatter prop_top_tier decade, mcolor(red)) ///
       (scatter prop_mid_tier decade, mcolor(blue)) ///
       (scatter prop_others decade, mcolor(green)), ///
       legend(order(1 "Top Tier" 2 "Mid Tier" 3 "Others"))
graph save "$image_path\Proportion of college by rank.png", replace

******Race******
cd"$dta_input"
use "race_prediction_nameandcounty.dta",clear
gen max_group = "" 
replace max_group = "whi" if pred_whi == max(pred_whi, pred_bla, pred_his, pred_asi, pred_oth)
replace max_group = "bla" if pred_bla == max(pred_whi, pred_bla, pred_his, pred_asi, pred_oth) & max_group == ""
replace max_group = "his" if pred_his == max(pred_whi, pred_bla, pred_his, pred_asi, pred_oth) & max_group == ""
replace max_group = "asi" if pred_asi == max(pred_whi, pred_bla, pred_his, pred_asi, pred_oth) & max_group == ""
replace max_group = "oth" if pred_oth == max(pred_whi, pred_bla, pred_his, pred_asi, pred_oth) & max_group == ""

* Bin the data by decades
gen decade = floor(year/10)*10

* Calculate the proportions for each group by decade
bys decade: gen decade_total = _N
egen count_whi_dec = total(max_group == "whi"), by(decade)
egen count_bla_dec = total(max_group == "bla"), by(decade)
egen count_his_dec = total(max_group == "his"), by(decade)
egen count_asi_dec = total(max_group == "asi"), by(decade)
egen count_oth_dec = total(max_group == "oth"), by(decade)
gen prop_whi_dec = count_whi_dec / decade_total
gen prop_bla_dec = count_bla_dec / decade_total
gen prop_his_dec = count_his_dec / decade_total
gen prop_asi_dec = count_asi_dec / decade_total
gen prop_oth_dec = count_oth_dec / decade_total

* Plot the proportions by decade
twoway (line prop_whi_dec decade, lcolor(red)) ///
       (line prop_bla_dec decade, lcolor(blue)) ///
       (line prop_his_dec decade, lcolor(green)) ///
       (line prop_asi_dec decade, lcolor(orange)) ///
       (line prop_oth_dec decade, lcolor(purple)) ///
       (scatter prop_whi_dec decade, mcolor(red) msize(small) ) ///
       (scatter prop_bla_dec decade, mcolor(blue) msize(small) ) ///
       (scatter prop_his_dec decade, mcolor(green) msize(small) ) ///
       (scatter prop_asi_dec decade, mcolor(orange) msize(small) ) ///
       (scatter prop_oth_dec decade, mcolor(purple) msize(small) ) ///
       , legend(label(1 "White") label(2 "Black") label(3 "Hispanic") label(4 "Asian") label(5 "Other")) ///
         ytitle("Proportion") xtitle("Decade") title("Proportion of Each Group by Decade")
graph save "$image_path\Proportion of Race.png", replace
