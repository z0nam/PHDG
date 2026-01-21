clear all

set more off

cd "/Users/namun/Library/CloudStorage/GoogleDrive-namun.cho@gmail.com/My Drive/2023_NW/_20230228_버블포착관련연구(장태석)/30.simulation"
local csvName _average_beta_ _beta_distribution_ _initial_wealth_ _final_wealth_ //_aggregated_

foreach csv in `csvName'{
    save `csv', emptyok replace
    local csvfiles: dir . files "*`csv'.csv"
    local isFirst = 1
    foreach csvfile in `csvfiles'{
        di "csvfile: `csvfile'"
        insheet using "`csvfile'", names clear
        rename v1 index
        local v2name = substr("`csvfile'", 1, 6)
        di "v2name=`v2name'"
        label var v2 "`v2name'"
        rename v2 `v2name'
        
        if `isFirst'==1 {
            save `csv', replace
        }
        else {
            merge 1:1 index using `csv', nogenerate
            save `csv', replace
        }

        local isFirst = 0
    }
    save `csv', replace
}

local vars argmax_wit top_agent_wealth_ratio k_ast_t gamma_t

clear all

local csv "_aggregated_.csv"

foreach var in `vars'{
    di "var: `var'"
    forvalues i=1/4{
        di "model: `i'"
        insheet using "Model`i'_aggregated_.csv", clear
        keep t `var'
        rename t index
        rename `var' Model`i'

        if `i'==1{
            save `var', replace
        }
        else{
            merge 1:1 index using `var', nogenerate
            save `var', replace
        }
    }
    order index Model1 Model2 Model3 Model4
    save `var', replace
}
