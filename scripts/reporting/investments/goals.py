import os
import argparse

from expectations import base_data
from configs import configs, main_ledger_file, prices_db
from utils import get_register_report, get_month_range, chart_builder
from utils import TOTAL_VALUE


def build_report(month_range, benchmark_report, mf_report):
	data = {}
	desired_length = 2
	for key in month_range:
		value = []
		if key in benchmark_report:
			value.append(benchmark_report[key][0])
		if key in mf_report:
			value.append(mf_report[key][TOTAL_VALUE])
		if len(value) == desired_length:
			data[key] = value
	return data


def argumentParser():
	parser = argparse.ArgumentParser(description='Optional app params')

	parser.add_argument('--config', type=str, choices=configs.keys(), 
		default='REAL_TTM', help='run different strategy for chart')

	return parser.parse_args()



accounts = 'Assets:MFs:Low-Volatility Assets:MFs:LargeMidCap Assets:MFs:Midcap-Momentum Assets:Sejal:MFs:Kotak-Low-Volatility Assets:Sejal:MFs:Zerodha-LargeMidCap Assets:Sejal:MFs:Kotak-Midcap-Momentum Assets:INDMoney:ETF Assets:Zerodha:Kite Assets:PF Assets:NPS'
PLOT_NAME = '/tmp/goals.png'


if __name__ == '__main__':
	args = argumentParser()
	month_range = get_month_range(configs[args.config]['start_date'], configs[args.config]['end_date'])
	investment_report = get_register_report(ledger_file = main_ledger_file, accounts = accounts, prices_db = prices_db)
	data = build_report(month_range, base_data, investment_report)
	plot_file = chart_builder(data, 'time', 'amount', ['expectations', 'current'], PLOT_NAME)
	os.system("~/.iterm2/imgcat -W 100% -H 100% {}".format(plot_file))
