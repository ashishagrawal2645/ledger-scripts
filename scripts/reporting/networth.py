import os
import subprocess
import multiprocessing as mp
from babel.numbers import format_currency

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


main_ledger_file = os.environ['LEDGER_MAIN_FILE']

fiscal_years = {
	'FY17' : '-e "2018/04/01"',
	'FY18' : '-e "2019/04/01"',
	'FY19' : '-e "2020/04/01"',
	'FY20' : '-e "2021/04/01"',
	'FY21' : '-e "2022/04/01"',
	'FY22' : '-e "2023/04/01"',
	'FY23' : '-e "2024/04/01"',
	'FY24' : '-e "2025/04/01"',
	'FY25' : '-e "2026/04/01"',
}

def get_balance(time_period):
	balance_generation = f'ledger -f {main_ledger_file} {time_period} -O bal -B -X INR -n Assets Liabilities | tail -n 1 | sed -e "s/ INR//g"'
	balance = subprocess.run(balance_generation, shell=True, capture_output=True, text=True).stdout
	return float(balance) if len(balance) > 0 else 0



def get_progress(kv_pair):
	key = kv_pair[0]
	value = kv_pair[1]
	bal = get_balance(value)

	return (key, bal)



def plot_graph(fiscal_data, xAxis_label, results):
	data = pd.DataFrame({
		xAxis_label : [key for key in fiscal_data], 
		"Increased YoY (in Millions)" : [results[key][1] for key in fiscal_data],
	})

	ax = sns.barplot(data=data, 
				  palette="husl", hue=xAxis_label, legend=False, 
				  x=xAxis_label, y="Increased YoY (in Millions)")
	for i in ax.containers:
		ax.bar_label(i,color='white', size=8, fmt = '%d')
	
	ax.xaxis.label.set_color('yellow')
	ax.tick_params(axis='x', colors='yellow')

	ax.yaxis.label.set_color('yellow')
	ax.tick_params(axis='y', colors='yellow')

	plt.savefig("/tmp/networth.png", dpi=300, transparent=True)
	os.system("~/.iterm2/imgcat -W 100% -H 100% /tmp/networth.png")



if __name__ == '__main__':

	fiscal_data = fiscal_years
	xAxis = "Years"

	pool = mp.Pool(mp.cpu_count())
	listOfTuples = [(key, fiscal_data[key]) for key in fiscal_data]
	res = pool.map_async(get_progress, listOfTuples)
	res.wait()

	results = {}
	for r in res.get():
		results[r[0]] = r[1]

	growthYoY = {}
	prev = 0
	lastKey = ''
	for key in results:
		if prev != 0:
			growthYoY[key] = (((results[key]/prev) - 1) * 100, results[key] - prev)
		prev = results[key]
		lastKey = key

	pool.close()
	plot_graph(growthYoY, xAxis, growthYoY)
	print("Overall networth : " + format_currency(int(results[lastKey]), 'INR', locale='en_IN'))


