import os
import re
import subprocess
from pyxirr import xirr
from datetime import datetime

from multiprocessing import Pool

dates = []
cashflows = []

benchmark_ledger_file = os.environ['LEDGER_ROOT']+'/entries/comparison_entries/benchmark-sip.ledger'


width_spacer = '{:22}'

def extract_dates_cashflows(txns, dates_list, cashflows_list):
	for entry in txns:
		if len(entry) > 0:
			entry = entry.split('\t')
			dates_list.append(datetime.strptime(entry[0], '%y-%b-%d').strftime('%Y-%m-%d'))
			cashflows_list.append(float(entry[1].strip()))


def add_transactions(key, dates_list, cashflows_list):
	transactions = subprocess.Popen(queries[key], shell=True, stdout=subprocess.PIPE).communicate()[0]
	if len(transactions) == 0:
		return
	transactions = transactions.decode('utf-8').split('\n')
	extract_dates_cashflows(transactions, dates_list, cashflows_list)


def add_bal(key, dates_list, cashflows_list):
	balance = subprocess.Popen(queries[key], shell=True, stdout=subprocess.PIPE).communicate()[0]
	if len(balance) == 0:
		return

	balance = float(balance.decode('utf-8').split('INR')[0].strip())
	dates_list.append(datetime.now().strftime('%Y-%m-%d'))
	cashflows_list.append(balance)



def include_last_6_months(dates_list, cashflows_list):
	add_transactions('last_6_months_investments', dates_list, cashflows_list)
	add_transactions('last_6_months_incomes', dates_list, cashflows_list)
	add_bal('last_6_months_balance', dates_list, cashflows_list)

def include_last_12_months(dates_list, cashflows_list):
	add_transactions('last_12_months_investments', dates_list, cashflows_list)
	add_transactions('last_12_months_incomes', dates_list, cashflows_list)
	add_bal('last_12_months_balance', dates_list, cashflows_list)

def include_last_18_months(dates_list, cashflows_list):
	add_transactions('last_18_months_investments', dates_list, cashflows_list)
	add_transactions('last_18_months_incomes', dates_list, cashflows_list)
	add_bal('last_18_months_balance', dates_list, cashflows_list)

def caller(func, message):
	dates_list = []
	cashflows_list = []
	func(dates_list, cashflows_list)
	dates.extend(dates_list)
	cashflows.extend(cashflows_list)
	if len(message) != 0:
		print(width_spacer.format(message) + ' : ' + str(round(xirr(dates_list, cashflows_list)*100, 2)) + " %")


queries = {
	'last_6_months_investments' : 'ledger -f ' + benchmark_ledger_file + ' -b "6 months ago" reg --cost --format "%d\t%(t) \n"  Equity:MFs:Benchmark | sed -e "s/ INR//g"',
	'last_6_months_incomes' : 'ledger -f ' + benchmark_ledger_file + ' -b "6 months ago" reg --format "%d\t%(amount) \n" Equity:PnL:Benchmark | sed -e \'s/ INR//g\'',
	'last_6_months_balance' : 'ledger -f ' + benchmark_ledger_file + ' -b "6 months ago" --invert -V --depth 2 bal Equity:MFs:Benchmark',

	'last_12_months_investments' : 'ledger -f ' + benchmark_ledger_file + ' -b "12 months ago" reg --cost --format "%d\t%(t) \n"  Equity:MFs:Benchmark | sed -e "s/ INR//g"',
	'last_12_months_incomes' : 'ledger -f ' + benchmark_ledger_file + ' -b "12 months ago" reg --format "%d\t%(amount) \n" Equity:PnL:Benchmark | sed -e \'s/ INR//g\'',
	'last_12_months_balance' : 'ledger -f ' + benchmark_ledger_file + ' -b "12 months ago" --invert -V --depth 2 bal Equity:MFs:Benchmark',
	
    'last_18_months_investments' : 'ledger -f ' + benchmark_ledger_file + ' -b "18 months ago" reg --cost --format "%d\t%(t) \n"  Equity:MFs:Benchmark | sed -e "s/ INR//g"',
	'last_18_months_incomes' : 'ledger -f ' + benchmark_ledger_file + ' -b "18 months ago" reg --format "%d\t%(amount) \n" Equity:PnL:Benchmark | sed -e \'s/ INR//g\'',
	'last_18_months_balance' : 'ledger -f ' + benchmark_ledger_file + ' -b "18 months ago" --invert -V --depth 2 bal Equity:MFs:Benchmark',
	
}


# This starts from 01st April, 2024 along with a few shares from the past.
# I have not included private equity in any other calculations so they will be excluded here as well
# Insurance gains will not be included
# Chinku's cash will not be included along with any interest income from savings accounts, etc

caller(include_last_6_months, 'Last 6 months')
caller(include_last_12_months, 'Last 12 months')
caller(include_last_18_months, 'Last 18 months')
# caller(include_indmoney_etfs, 'INDMoney ETFs')
# caller(include_PPF, 'PPF')
# caller(include_EPF, 'EPF')
# caller(include_emergency_fd, 'FDs')
# caller(include_real_estate, 'Real estate')
# caller(include_gold_bar, 'Gold')

print(width_spacer.format('Overall') + ' : ' + str(round(xirr(dates, cashflows)*100, 2)) + " %")





# ledger -f $LEDGER_ROOT/entries/comparison_entries/benchmark-sip.ledger --begin "12 months ago"  --average-lot-prices bal Benchmark