clear all

local csvName _average_beta_ _beta_distribution_ _initial_wealth_ _final_wealth_ k_ast_t argmax_wit gamma_t top_agent_wealth_ratio
/*

1 _average_beta_
2 _beta_distribution_
3 _initial_wealth_
4 _final_wealth_
5 k_ast_t
6 argmax_wit
7 gamma_t
8 top_agent_wealth_ratio

*/
local total_number_model 4

tokenize "`csvName'"

use `1', clear

tsset index
rename index Round
forvalues i = 1/`total_number_model'{
    tsline Model`i', name("Model`i'") tlabel(,labsize(large)) ylabel(,labsize(large)) lwidth(thick) yline(0.8, lcolor(red) lwidth(thick) lpattern(dash)) xtitle(,size(large)) ytitle(,size(large))
}
graph combine Model1 Model2 Model3 Model4
graph export "`1'_combine.png", replace


use `2', clear

forvalues i = 1/`total_number_model'{
    hist Model`i', name("`2'Model`i'") xlabel(,labsize(large)) ylabel(,labsize(large)) percent     xtitle(,size(large)) ytitle(,size(large))
}
graph combine `2'Model1 `2'Model2 `2'Model3 `2'Model4
graph export "`2'_combine.png", replace


use `3', clear

forvalues i = 1/`total_number_model'{
    egen sd_Model`i' = sd(Model`i')
    if sd_Model`i'==0 {
        hist Model`i' , start(100) width(10) xsc(r(0 200)) xla(100) xlabel(,labsize(large)) ylabel(,labsize(large)) percent name("`3'Model`i'") xtitle(,size(large)) ytitle(,size(large))
    } 
    else {
        hist Model`i', name("`3'Model`i'") percent xlabel(,labsize(large)) ylabel(,labsize(large)) xtitle(,size(large)) ytitle(,size(large))
    }
}
graph combine `3'Model1 `3'Model2 `3'Model3 `3'Model4
graph export "`3'_combine.png", replace


use `4', clear

forvalues i = 1/`total_number_model'{
    rename Model`i' final_wealth_model`i'
    label var final_wealth_model`i' "Final Wealth"
}
merge 1:1 index using `2'
forvalues i = 1/`total_number_model'{
    rename Model`i' beta_model`i'
    label var beta_model`i' "Propensity to Risky Asset (Model `i')"
}


forvalues i = 1/`total_number_model'{
    // gen log_model_`i' = log(Model`i')
    scatter final_wealth_model`i' beta_model`i', name("`4'Model`i'") xline(0.8, lcolor(red) lwidth(thick) lpattern(dash)) xtitle(,size(large)) ytitle(,size(large))
}
graph combine `4'Model1 `4'Model2 `4'Model3 `4'Model4
graph export "`4'_combine.png", replace

forvalues i = 1/`total_number_model'{
    gen lfinal_wealth_model`i' = log(final_wealth_model`i')
    label var lfinal_wealth_model`i' "Log of Final Wealth"
    scatter lfinal_wealth_model`i' beta_model`i', name("`4'lModel`i'") xlabel(,labsize(large)) ylabel(,labsize(large)) xline(0.8, lcolor(red) lwidth(thick) lpattern(dash)) xtitle(,size(large)) ytitle(,size(large))
}

graph combine `4'lModel1 `4'lModel2 `4'lModel3 `4'lModel4
graph export "log_`4'_combine.png", replace


/*

1 _average_beta_
2 _beta_distribution_
3 _initial_wealth_
4 _final_wealth_
5 k_ast_t
6 argmax_wit
7 gamma_t
8 top_agent_wealth_ratio

*/
use `5', clear

tsset index
rename index Round
drop if Round == 0
forvalues i = 1/`total_number_model'{
    tsline Model`i', name("`5'Model`i'") tlabel(,labsize(large)) ylabel(,labsize(large)) lwidth(thick) yline(0.8, lcolor(red) lwidth(thick) lpattern(dash)) xtitle(,size(large)) ytitle(,size(large))
}
graph combine `5'Model1 `5'Model2 `5'Model3 `5'Model4
graph export "`5'_combine.png", replace

use `7', clear

tsset index
rename index Round
forvalues i = 1/`total_number_model'{
    gen gamma_t_Model`i' = Round/Model`i'
    label var gamma_t_Model`i' "Model`i'"
    tsline gamma_t_Model`i', name("`7'Model`i'") tlabel(,labsize(large)) ylabel(,labsize(large)) lwidth(thick) xtitle(,size(large)) ytitle(,size(large))
}
graph combine `7'Model1 `7'Model2 `7'Model3 `7'Model4
graph export "`7'_combine.png", replace


use `8', clear

tsset index
rename index Round
forvalues i = 1/`total_number_model'{
    tsline Model`i', name("`8'Model`i'") tlabel(,labsize(large)) ylabel(,labsize(large)) lwidth(thick) xtitle(,size(large)) ytitle(,size(large))
}
graph combine `8'Model1 `8'Model2 `8'Model3 `8'Model4
graph export "`8'_combine.png", replace
