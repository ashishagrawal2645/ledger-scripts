import os
import argparse
from babel.numbers import format_currency

from configs import configs, main_ledger_file, benchmark_ledger_file, prices_db
from utils import get_register_report, get_month_range, chart_builder
from utils import TOTAL_VALUE


def build_report(month_range, reports, field):
	data = {}
	latest_value = []
	desired_length = len(reports)
	for key in month_range:
		value = []
		for report in reports:
			if key in report:
				value.append(report[key][field])
		if len(value) == desired_length:
			data[key] = value
			latest_value = value
	return (data,latest_value)


def argumentParser():
	parser = argparse.ArgumentParser(description='Optional app params')

	parser.add_argument('--config', type=str, choices=configs.keys(), 
		default='REAL_TTM', help='run different strategy for chart')

	return parser.parse_args()


accounts = ('Assets:Sejal:MFs Assets:MFs:Low-Volatility Assets:MFs:LargeMidCap Assets:MFs:Midcap-Momentum', 'Equity:MFs:Benchmark')
PLOT_NAME = '/tmp/performance.png'


if __name__ == '__main__':
	args = argumentParser()
	month_range = get_month_range(configs[args.config]['start_date'], configs[args.config]['end_date'])
	investment_report = get_register_report(ledger_file = main_ledger_file, accounts = accounts[0], prices_db = prices_db)
	benchmark_report = get_register_report(ledger_file = benchmark_ledger_file, accounts = accounts[1], prices_db = prices_db)
	(final_report,latest_values) = build_report(month_range, [investment_report, benchmark_report], TOTAL_VALUE)
	plot_file = chart_builder(final_report, 'time', 'amount', ['Investment', 'Benchmark'], PLOT_NAME)
	os.system("~/.iterm2/imgcat -W 95% -H 95% {}".format(plot_file))
	gains = (latest_values[0] - latest_values[1])/100000
	print("Gains over benchmark : " + format_currency(gains, 'INR', locale='en_IN') + " lacs")
	# os.system('qlmanage -p {}'.format(plot_file))




