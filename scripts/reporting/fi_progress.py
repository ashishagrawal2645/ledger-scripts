#!/usr/bin/env python3

import os
import subprocess
import multiprocessing as mp
from datetime import date
import itertools
import argparse


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


main_ledger_file = os.environ['LEDGER_MAIN_FILE']

income_accounts = 'Income:Dividends Income:Growpital Income:House1 Income:Interest Income:PnL:MF Income:PnL:Stocks Income:Insurance Income:Others Equity:Diners:Reward-Points:Used Equity:Diners:Discount:Others'
expenses_accounts_to_exclude = 'Expenses:Taxes Expenses:Taxes:Professional-Tax Expenses:Donation:Political'

fiscal_years = {
	'FY18' : '-b "2018/04/01" -e "2019/04/01"',
	'FY19' : '-b "2019/04/01" -e "2020/04/01"',
	'FY20' : '-b "2020/04/01" -e "2021/04/01"',
	'FY21' : '-b "2021/04/01" -e "2022/04/01"',
	'FY22' : '-b "2022/04/01" -e "2023/04/01"',
	'FY23' : '-b "2023/04/01" -e "2024/04/01"',
	'FY24' : '-b "2024/04/01" -e "2025/04/01"',
	'FY25' : '-b "2025/04/01" -e "2026/04/01"',
}

fiscal_months = {
	'Apr' : '-b "2025/04/01" -e "2025/05/01"',
	'May' : '-b "2025/04/01" -e "2025/06/01"',
	'Jun' : '-b "2025/04/01" -e "2025/07/01"',
	'Jul' : '-b "2025/04/01" -e "2025/08/01"',
	'Aug' : '-b "2025/04/01" -e "2025/09/01"',
	'Sep' : '-b "2025/04/01" -e "2025/10/01"',
	'Oct' : '-b "2025/04/01" -e "2025/11/01"',
	'Nov' : '-b "2025/04/01" -e "2025/12/01"',
	'Dec' : '-b "2025/04/01" -e "2026/01/01"',
	'Jan' : '-b "2025/04/01" -e "2026/02/01"',
	'Feb' : '-b "2025/04/01" -e "2026/03/01"',
	'Mar' : '-b "2025/04/01" -e "2026/04/01"',
}

def trim_fiscal_months(fiscal_months):
	return dict(itertools.islice(fiscal_months.items(), (date.today().month-4)%12+1))


def get_balance(time_period, account):
	balance_generation = f'ledger -f {main_ledger_file} --effective {time_period} -O bal -B -X INR --format "%(T) \n" --depth 1 {account} | tail -n 1 | sed -e "s/ INR//g"'
	balance = subprocess.run(balance_generation, shell=True, capture_output=True, text=True).stdout
	return float(balance) if len(balance) > 0 else 0



def get_progress(kv_pair):
	key = kv_pair[0]
	value = kv_pair[1]
	income_total = -1 * get_balance(value, income_accounts)

	expenses_total = get_balance(value, 'Expenses')
	expenses_total -= get_balance(value, expenses_accounts_to_exclude)
	return (key, str(round((income_total*100)/expenses_total, 2)))



def plot_graph(fiscal_months, xAxis_label, results):
	data = pd.DataFrame({
		xAxis_label : [key for key in fiscal_months], 
		"Progress (in %)" : [float(results[key]) for key in fiscal_months],
	})

	ax = sns.barplot(data=data, 
				  palette="husl", hue=xAxis_label, legend=False,
				  x=xAxis_label, y="Progress (in %)")
	for i in ax.containers:
		ax.bar_label(i,color='white', size=9)
	# plt.show()
	
	ax.xaxis.label.set_color('yellow')
	ax.tick_params(axis='x', colors='yellow')

	ax.yaxis.label.set_color('yellow')
	ax.tick_params(axis='y', colors='yellow')

	plt.savefig("/tmp/fi-progress.png", dpi=300, transparent=True)
	os.system("~/.iterm2/imgcat -W 100% -H 100% /tmp/fi-progress.png")



def argumentParser():
	parser = argparse.ArgumentParser(description='Optional app params')

	# Switch
	parser.add_argument('--yearly', action='store_true',
	                    help='run execution for fiscal years')

	return parser.parse_args()

if __name__ == '__main__':
	args = argumentParser()

	fiscal_data = {}
	xAxis = ""

	if args.yearly:
		fiscal_data = fiscal_years
		xAxis = "Years"
	else:
		fiscal_data = trim_fiscal_months(fiscal_months)
		xAxis = "Months"

	pool = mp.Pool(mp.cpu_count())
	listOfTuples = [(key, fiscal_data[key]) for key in fiscal_data]
	res = pool.map_async(get_progress, listOfTuples);
	res.wait()

	results = {}
	for r in res.get():
		results[r[0]] = r[1]

	pool.close()
	plot_graph(fiscal_data, xAxis, results)
		

