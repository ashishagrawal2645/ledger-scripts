#!/bin/zsh

BEGIN=$1
END=$2

if [ -z $1 ]; then
	BEGIN=`date '+%Y/01/01'`
fi

if [ -z $2 ]; then
	END=`date '+%Y/12/31'`
fi

ledger -f $LEDGER_MAIN_FILE -b "$BEGIN" -e "$END" bal --invert --depth 3 liabilities:creditcard:hdfc$ liabilities:creditcard:hdfc:others$ | sed -e 's/^ *//' | cut -d ' ' -f 1
