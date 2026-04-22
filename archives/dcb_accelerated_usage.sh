#!/bin/zsh

BEGIN=$1
END=$2

if [ -z $1 ]; then
	BEGIN=`date '+%Y/%m/01'`
fi

if [ -z $2 ]; then
	END=`date -v +1m '+%Y/%m/01'`
fi

ledger -f $LEDGER_MAIN_FILE -b "$BEGIN" -e "$END" bal --limit 'has_tag(/accelerated/) and account=~/Equity:Diners:Reward-Points/'
