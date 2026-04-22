import os
import subprocess
import argparse

import matplotlib.pyplot as plt # type: ignore
from matplotlib.gridspec import GridSpec
import pandas as pd
import seaborn as sns # type: ignore


def get_bal(account, label, cost_basis = False):
	valuation = '-B' if cost_basis else '-V'
	query = f'ledger -f {main_ledger_file} --price-db {prices_db} {valuation} -X INR --depth 1 --format "%(market(display_total))\n%/" bal {account}'
	balance = subprocess.run(query, shell=True, capture_output=True, text=True).stdout
	amount = 0
	if len(balance) > 0:
		amount = float(balance.split(' INR')[0])
	return (label, amount)


def getChart(report):
	plot_file = '/tmp/all_assets.png'
	plot_title = 'Tracker'
	labels = list(report.keys())
	values = list(map(lambda x: report[x], labels))
	data = pd.DataFrame({'labels': labels, 'values': values})
	colors = sns.color_palette("pastel")
	plt.pie(data=data, x='values', labels=labels, colors=colors, autopct="%0.0f%%", textprops=dict(color="white"))
	plt.title(plot_title, color='#B87C4C')
	plt.savefig(plot_file, dpi=300, transparent=True)
	return plot_file


def getPortfolioChart(reports):
	plot_file = '/tmp/all_assets.png'

	fig = plt.figure()
	gs = GridSpec(2, 2, figure=fig)

	ax1 = fig.add_subplot(gs[0, :])
	ax2 = fig.add_subplot(gs[1, 0])
	ax3 = fig.add_subplot(gs[1, 1])


	all_axes = [ax1, ax2, ax3]
	titles = ['Overall', 'Core', 'Satellite']
	colors = sns.color_palette("pastel")
	
	for i in range(3):
		report = reports[i]
		curr_plot = all_axes[i]
		labels = list(report.keys())
		values = list(map(lambda x: report[x], labels))
		data = pd.DataFrame({'labels': labels, 'values': values})
	
		curr_plot.pie(data=data, x='values', labels=labels, colors=colors, autopct="%0.0f%%", textprops=dict(color="white"))
		curr_plot.set_title(titles[i], color='#B87C4C')

	plt.tight_layout()
	plt.savefig(plot_file, dpi=300, transparent=True)
	return plot_file


def listToMap(report):
	result = {}
	for data in report:
		account = data[0]
		amount = data[1]
		if account in result:
			result[account] = result[account] + amount
		else:
			result[account] = amount
	return result


def argumentParser():
	parser = argparse.ArgumentParser(description='Optional app params')

	# Switch
	parser.add_argument('--cost-basis', action='store_true',
	                    help='run execution for cost basis i.e. investment amount rather than current valuations')

	parser.add_argument('--config', type=str, choices=configs.keys(), 
		default='CLASS_LEVEL', help='run different strategy for chart')
	
	parser.add_argument('--portfolio', action='store_false',
	                    help='run execution portfolio displaying 3 charts')

	return parser.parse_args()



main_ledger_file = os.environ['LEDGER_MAIN_FILE']
prices_db = os.environ['LEDGER_ROOT']+'/entries/comparison_entries/index_prices'

configs = {
	'CLASS_LEVEL' : {
		'Assets:MFs'                                 : 'Domestic Equity (45%)',
		'Assets:Sejal:MFs'                           : 'Domestic Equity (45%)',
		'Assets:NPS:Equity'                          : 'Domestic Equity (45%)',
		'Assets:Zerodha:Kite:MFs:NASDAQ'             : 'International Equity (11%)',
		'Assets:INDMoney:ETF'                        : 'International Equity (11%)',
		'Assets:PF'                                  : 'Debt (24%)',
		'Assets:Sbi:PPF'                             : 'Debt (24%)',
		'Assets:NPS:Corp-Debt'                       : 'Debt (24%)',
		'Assets:NPS:Govt-Bonds'                      : 'Debt (24%)',
		'Assets:Zerodha:Kite:GP'                     : 'Stocks (5%)',
		'Assets:Zerodha:Kite:Self'                   : 'Stocks (5%)',
		'Assets:Commodity'                           : 'Stocks (5%)',
		'Assets:Gold:Bar'                            : 'Gold (5%)',
		'Assets:Zerodha:Kite:MFs:Gold'               : 'Gold (5%)',
		'Assets:Sejal:FD'                            : 'Cash (5%)',
		'Assets:Sejal$'                              : 'Cash (5%)',
		'Assets:IDFC:Account'                        : 'Cash (5%)',
		'Assets:Plot'                                : 'Real Estate (5%)',
	},
	'MF_LEVEL' : {
		'Assets:MFs:Low-Volatility'                  : 'Low-Volatility (35%)',
		'Assets:Sejal:MFs:Kotak-Low-Volatility'      : 'Low-Volatility (35%)',
		'Assets:MFs:LargeMidCap'                     : 'LargeMidCap (30%)',
		'Assets:Sejal:MFs:Zerodha-LargeMidCap'       : 'LargeMidCap (30%)',
		'Assets:MFs:Midcap-Momentum'                 : 'Midcap-Momentum (35%)',
		'Assets:Sejal:MFs:Kotak-Midcap-Momentum'     : 'Midcap-Momentum (35%)',
	},
	


	'CORE_SATELLITE' : {
		'Assets:MFs'                                 : 'Core (80%)',
		'Assets:Sejal:MFs'                           : 'Core (80%)',
		'Assets:Sejal:SIF'                           : 'Core (80%)',
		'Assets:Zerodha:Kite:MFs:NASDAQ'             : 'Core (80%)',
		'Assets:INDMoney:ETF'                        : 'Core (80%)',
		'Assets:NPS'                                 : 'Core (80%)',
		'Assets:PF'                                  : 'Core (80%)',
		'Assets:Sbi:PPF'                             : 'Core (80%)',
		'Assets:Zerodha:Account'                     : 'Satellite (20%)',
		'Assets:Zerodha:Kite:GP'                     : 'Satellite (20%)',
		'Assets:Zerodha:Kite:Self'                   : 'Satellite (20%)',
		'Assets:Zerodha:Kite:MFs:Gold'               : 'Satellite (20%)',
		'Assets:Commodity'                           : 'Satellite (20%)',
		'Assets:Gold:Bar'                            : 'Satellite (20%)',
		'Assets:Plot'                                : 'Satellite (20%)',
		'Assets:Sejal:FD'                            : 'Satellite (20%)',
		'Assets:Sejal$'                              : 'Satellite (20%)',
		'Assets:IDFC:Account'                        : 'Satellite (20%)',
	},
	
	'CORE_PORTFOLIO' : {
		'Assets:MFs'                                 : 'Domestic (56%)',
		'Assets:Sejal:MFs'                           : 'Domestic (56%)',
		'Assets:Sejal:SIF:Altiva'                    : 'Domestic (56%)',
		'Assets:Sejal:SIF:Isif'                      : 'Domestic (56%)',
		'Assets:NPS:Equity'                          : 'Domestic (56%)',
		'Assets:Zerodha:Kite:MFs:NASDAQ'             : 'International (14%)',
		'Assets:INDMoney:ETF'                        : 'International (14%)',
		'Assets:PF'                                  : 'Debt (30%)',
		'Assets:Sbi:PPF'                             : 'Debt (30%)',
		'Assets:NPS:Corp-Debt'                       : 'Debt (30%)',
		'Assets:NPS:Govt-Bonds'                      : 'Debt (30%)',
		'Assets:Sejal:SIF:MOS-Arbitrate'             : 'Debt (30%)',
	},
	'SATELLITE_PORTFOLIO' : {
		'Assets:Zerodha:Kite:GP'                     : 'Stocks',
		'Assets:Zerodha:Kite:Self'                   : 'Stocks',
		'Assets:Commodity'                           : 'Stocks',
		'Assets:Gold:Bar'                            : 'Gold',
		'Assets:Zerodha:Kite:MFs:Gold'               : 'Gold',
		'Assets:Plot'                                : 'Real Estate',
		'Assets:Sejal:FD'                            : 'Cash (5%)',
		'Assets:Sejal$'                              : 'Cash (5%)',
		'Assets:IDFC:Account'                        : 'Cash (5%)',
		'Assets:Zerodha:Account'                     : 'Cash (5%)',
	},
}

if __name__ == '__main__':
	args = argumentParser()
	if(args.portfolio):
		report = listToMap(map(lambda item: get_bal(item[0], item[1], args.cost_basis) , configs[args.config].items()))
		plot_file = getChart(report)
		os.system("~/.iterm2/imgcat -W 100% -H 95% {}".format(plot_file))
	else:
		report1 = listToMap(map(lambda item: get_bal(item[0], item[1], True) , configs['CORE_SATELLITE'].items()))
		report2 = listToMap(map(lambda item: get_bal(item[0], item[1], True) , configs['CORE_PORTFOLIO'].items()))
		report3 = listToMap(map(lambda item: get_bal(item[0], item[1], True) , configs['SATELLITE_PORTFOLIO'].items()))
		plot_file = getPortfolioChart([report1,report2,report3])
		os.system("~/.iterm2/imgcat -W 100% -H 95% {}".format(plot_file))



