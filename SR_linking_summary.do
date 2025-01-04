cd "C:/Users/87208/Documents/Documents/RA/Social register/dta_output"
use "Social Registers_long_matched_NY_v3.dta", clear

* Sort the dataset by 'year' and 'match_as_master'
sort year match_as_master
replace match_as_master = "null" if match_as_master == ""
bys year match_as_master: egen count_type = count(match_as_master)
bys year: egen total_count = count(year)

* Calculate the percentage
gen percent = (count_type / total_count) * 100

* Collapse the dataset to get a summary table
collapse (mean) total_count count_type percent, by(year match_as_master)

* Calculate the average statistics for the entire dataset
replace count_type = . if year == 1958
replace percent = . if year == 1958
egen avg_count_type = mean(count_type), by(match_as_master)
egen avg_percent = mean(percent), by(match_as_master)

format avg_count_type %9.3f
format avg_percent %9.3f
format total_count %9.3f

* For Excel
export excel using "summary.xlsx", firstrow(variables) replace

