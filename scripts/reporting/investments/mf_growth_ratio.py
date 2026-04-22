import os
import argparse

from configs import configs, main_ledger_file, prices_db
from utils import get_register_report, get_month_range, chart_builder
from utils import MONTHLY_VALUE, TOTAL_VALUE


def build_report(month_range, report):
	data = {}
	total = 0
	for key in month_range:
		if key in report:
			total += report[key][MONTHLY_VALUE]
			data[key] = [report[key][TOTAL_VALUE]/total]
	return data


def argumentParser():
	parser = argparse.ArgumentParser(description='Optional app params')

	parser.add_argument('--config', type=str, choices=configs.keys(), 
		default='REAL_TTM', help='run different strategy for chart')

	return parser.parse_args()


accounts = 'Assets:Sejal:MFs Assets:MFs:Low-Volatility Assets:MFs:LargeMidCap Assets:MFs:Midcap-Momentum'
PLOT_NAME = '/tmp/ratio.png'


if __name__ == '__main__':
	args = argumentParser()
	start_date = configs[args.config]['start_date']
	month_range = get_month_range(configs[args.config]['start_date'], configs[args.config]['end_date'])
	investment_report = get_register_report(ledger_file = main_ledger_file, accounts = accounts, prices_db = prices_db, start_date=start_date)
	final_report = build_report(month_range, investment_report)
	plot_file = chart_builder(final_report, 'time', 'percentage', ['Ratio of market value to investment'], PLOT_NAME)
	os.system("~/.iterm2/imgcat -W 100% -H 100% {}".format(plot_file))




