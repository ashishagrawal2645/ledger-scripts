#!/bin/bash

export LEDGER_ROOT=${HOME}'/ledger'
export LEDGER_FILE=${LEDGER_ROOT}'/entries/current.ledger'
export LEDGER_MAIN_FILE=${LEDGER_ROOT}'/entries/main.'${LEDGER_CONFIG_PREFIX}'ledger'

alias fava-ledger=${LEDGER_ROOT}'/scripts/ops/fava_ledger.sh'
alias fava-accounts=${LEDGER_ROOT}'/scripts/ops/fava_accounts.sh'
alias ledger-debug=${LEDGER_ROOT}'/scripts/ops/ledger_debug.sh'
alias ledger-equity=${LEDGER_ROOT}'/scripts/ops/ledger_equity.sh'

alias ledger-main='ledger -f '${LEDGER_MAIN_FILE}

# Reporting related scripts
export LEDGER_REPORTS=${LEDGER_ROOT}/scripts/reporting

# alias budget='python3 '${LEDGER_REPORTS}'/budget_report.py'
# alias cg-valuation=${LEDGER_REPORTS}'/house1_valuation.sh'
# alias cc-bal=${LEDGER_REPORTS}'/creditcard_bal.sh'
# alias accelerated-rewards-usage=${LEDGER_REPORTS}'/dcb_accelerated_usage.sh'
# alias dcb-usage=${LEDGER_REPORTS}'/dcb_usage.sh'

alias liabilities=${LEDGER_REPORTS}'/liabilities.sh'
alias rewards='python3 '${LEDGER_REPORTS}'/reward_points.py'
alias lots_balances='python3 '${LEDGER_REPORTS}'/lot_balances.py'
alias fi-progress='python3 '${LEDGER_REPORTS}'/fi_progress.py'
alias cc-discount='python3 '${LEDGER_REPORTS}'/cc_discount.py'
alias consolidate-virtual-txns='python3 '${LEDGER_REPORTS}'/consolidate_virtual_postings.py'


alias balance-report='python3 '${LEDGER_REPORTS}'/balance_report.py'
alias cc-usage='python3 '${LEDGER_REPORTS}'/cc_milestones.py'
alias xirr='python3 '${LEDGER_REPORTS}'/xirr.py'
alias expenses-report='python3 '${LEDGER_REPORTS}'/expenses_report.py'
alias networth='python3 '${LEDGER_REPORTS}'/networth.py'

alias overall-asset-allocation=${LEDGER_REPORTS}'/asset_allocation_overall.sh'
alias labelled-asset-allocation='python3 '${LEDGER_REPORTS}'/investments/asset_allocation_labelled.py'

alias mf-performance='python3 '${LEDGER_REPORTS}'/investments/mf_performance.py'
alias mf-growth='python3 '${LEDGER_REPORTS}'/investments/mf_growth_ratio.py'

alias retirement-tracker='python3 '${LEDGER_REPORTS}'/investments/goals.py'

alias portfolio-performance='python '${LEDGER_REPORTS}'/portfolio/nifty_comparison.py'
alias fetch-nifty-historical-data='python '${LEDGER_REPORTS}'/portfolio/historical_data.py'


# short hand aliases for regular use
alias nw='networth'
alias exp='expenses-report'
alias cost-basis-allocation='labelled-asset-allocation --cost-basis'
alias valuation-basis-allocation='labelled-asset-allocation'
alias mf-allocation='labelled-asset-allocation --config MF_LEVEL'
alias portfolio-allocation='labelled-asset-allocation --portfolio'
alias cspdcl='ledger-main --effective reg -M -b "2024/05/01" Liabilities:Chinku:Electricity'




alias fire='fi-progress'
alias allocation='overall-asset-allocation'

alias documentation='python3 '${LEDGER_ROOT}'/scripts/documentation.py'

= () {
    printf "%.2f \n" $(echo $@ | bc -l)
}

# needed so that outputs are printed in stdout
export PAGER='less'
export LESS="-F -X -R"


