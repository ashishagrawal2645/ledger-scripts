import os
import subprocess
import re
from datetime import datetime
from datetime import date
import calendar

from functools import reduce

import matplotlib.pyplot as plt # type: ignore
import pandas as pd
import seaborn as sns # type: ignore

DATE_AMOUNT_REGEX = r'(\d{2})-(\w{3})-\d{2} - \d{2}-\w{3}-\d{2}\s+(.*)'

TOTAL_VALUE = 'total_value'
MONTHLY_VALUE = 'month_value'


def get_register_report(ledger_file, accounts, start_date = None, end_date = None, prices_db = None, dates_to_filter = None):
	ledger_command = build_command(ledger_file, accounts, start_date, end_date, prices_db, dates_to_filter)
	report = subprocess.run(ledger_command, shell=True, capture_output=True, text=True).stdout
	report_lines = report.split('\n')[:-1]
	report_data = reduce(parse_report_row, report_lines, {})
	return report_data

DATE_AMOUNT_REGEX = r'(\d{2})-(\w{3})-\d{2} - \d{2}-\w{3}-\d{2}\s+(.*)'

def build_command(ledger_file, accounts, start_date, end_date, prices_db, dates_to_filter):
	if accounts == None:
		raise Exception('accounts cannot be empty')
	base = 'ledger'
	file = f' -f {ledger_file}' if ledger_file else ''
	begin_date = f' -b {start_date.strftime("%Y-%m-%d")}' if start_date else ''
	ending_date = f' -e {end_date.strftime("%Y-%m-%d")}' if end_date else ''
	flags = ' -M -V -X INR --no-revalued --depth 1'
	prices = f' --price-db {prices_db}' if prices_db else ''
	register = ' reg'
	accounts_filter = f' {accounts}' if accounts else ''
	return base + file + begin_date + ending_date + flags + prices + register + accounts_filter


def parse_report_row(data_dict, row):
	match = re.search(DATE_AMOUNT_REGEX, row)
	year = match.group(1)
	month = match.group(2)
	rest = match.group(3).split(' INR')
	investment = rest[0].split(' ')[-1].strip()
	market_value = rest[1].strip()
	key = month + '-' + year
	if len(investment) > 0 and len(market_value)>0:
		data_dict[key] = {
			MONTHLY_VALUE: float(investment),
			TOTAL_VALUE: float(market_value),
		}
	return data_dict


def get_month_range(start_date, end_date):
	end_date_key = end_date.strftime("%b-%y")
	count = 0
	result = []
	while True:
		curr_date = add_months(start_date, count)
		curr_date_key = curr_date.strftime("%b-%y")
		if curr_date_key == end_date_key:
			break
		result.append(curr_date_key)
		count += 1
	return result


def get_last_day_of_current_month():
    """
    Returns the last day of the current month as a date object.
    """
    today = date.today()
    year = today.year
    month = today.month
    
    # monthrange returns a tuple: (weekday of first day, number of days in month)
    # We are interested in the second element (number of days)
    _, num_days = calendar.monthrange(year, month)
    
    last_day_of_month = date(year, month, num_days)
    return last_day_of_month


def add_months(current_date, months_to_add):
	year = current_date.year + (current_date.month + months_to_add - 1) // 12
	month = (current_date.month + months_to_add - 1) % 12 + 1
	try:
		return datetime(year, month, current_date.day, current_date.hour, current_date.minute, current_date.second)
	except:
		_, num_days = calendar.monthrange(year, month)
		return datetime(current_date.year + (current_date.month + months_to_add - 1) // 12,
                        (current_date.month + months_to_add - 1) % 12 + 1,
                        num_days, current_date.hour, current_date.minute, current_date.second)
	


def get_ttm_date(current_date):
	new_date = datetime(current_date.year - 1, current_date.month, 1)
	return new_date


def get_ttm_with_curr_date(current_date):
	next_month = add_months(current_date, 1)
	return get_ttm_date(next_month)

def reset_to_first_day_of_month(current_date):
	new_date = datetime(current_date.year, current_date.month, 1)
	return new_date


def chart_builder(report, x_label, y_label, columns, plot_file):
	data = pd.DataFrame.from_dict(data=report, orient='index', columns=columns)
	sns.set_style('whitegrid', {"grid.color": ".3", "grid.linestyle": ":"})
	ax = sns.lineplot(data=data, dashes=False)
	
	xticks = ax.get_xticks()
	if len(xticks) > 15:
		ax.set_xticks(xticks[::len(xticks) // 15])

	ax.set_xlabel(x_label)
	ax.xaxis.label.set_color('yellow')
	ax.tick_params(axis='x', colors='yellow', labelrotation=45)

	ax.set_ylabel(y_label)
	ax.yaxis.label.set_color('yellow')
	ax.tick_params(axis='y', colors='yellow')
	
	plt.savefig(plot_file, dpi=300, transparent=True)
	return plot_file


if __name__ == '__main__':
	main_ledger_file = os.environ['LEDGER_MAIN_FILE']
	prices_db = os.environ['LEDGER_ROOT']+'/entries/comparison_entries/index_prices'
	start_date = '2023/04/01'
	accounts = ('Assets:MFs:Low-Volatility Assets:MFs:LargeMidCap Assets:MFs:Midcap-Momentum', 'Equity:MFs:Benchmark')
	print(get_register_report(main_ledger_file, accounts[0], start_date, prices_db))