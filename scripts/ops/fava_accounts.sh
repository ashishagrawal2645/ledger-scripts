ledger -f ${LEDGER_MAIN_FILE} accounts --flat | awk '{print "1970-01-01 open " $0}' | sed  "s/Equity:Opening-Balances/Equity:Opening-Balances/g" > ${LEDGER_ROOT}/entries/accounts.beancount
