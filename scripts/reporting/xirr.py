import os
import re
import subprocess
from pyxirr import xirr
from datetime import datetime

from multiprocessing import Pool

dates = []
cashflows = []

main_ledger_file = os.environ['LEDGER_MAIN_FILE']


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



def include_kuvera_mf(dates_list, cashflows_list):
	add_transactions('Kuvera_MFs_Investments', dates_list, cashflows_list)
	add_transactions('Kuvera_MFs_Incomes', dates_list, cashflows_list)
	add_bal('Kuvera_MFs_Current_Balance', dates_list, cashflows_list)

def include_indmoney_etfs(dates_list, cashflows_list):
	add_transactions('INDMoney_Investments', dates_list, cashflows_list)
	add_transactions('INDMoney_Incomes', dates_list, cashflows_list)
	add_bal('INDMoney_Current_Balance', dates_list, cashflows_list)

def include_nps(dates_list, cashflows_list):
	add_transactions('NPS_Investments', dates_list, cashflows_list)
	add_transactions('NPS_Incomes', dates_list, cashflows_list)
	add_bal('NPS_Current_Balance', dates_list, cashflows_list)

def include_EPF(dates_list, cashflows_list):
	add_transactions('EPF_Deposits', dates_list, cashflows_list)
	add_transactions('EPF_Interest', dates_list, cashflows_list)
	add_bal('EPF_Net_Principal_Balance', dates_list, cashflows_list)

def include_PPF(dates_list, cashflows_list):
	add_transactions('PPF_Deposits', dates_list, cashflows_list)
	add_transactions('PPF_Interest', dates_list, cashflows_list)
	add_bal('PPF_Net_Principal_Balance', dates_list, cashflows_list)

def include_Zerodha_Shares(dates_list, cashflows_list):
	add_transactions('Zerodha_Shares_Investments', dates_list, cashflows_list)
	add_transactions('Zerodha_prev_fy_Investments', dates_list, cashflows_list)
	add_transactions('Zerodha_Shares_Gains', dates_list, cashflows_list)
	add_transactions('Zerodha_Shares_Dividends', dates_list, cashflows_list)
	add_bal('Zerodha_Shares_Current_Balance', dates_list, cashflows_list)

def include_real_estate(dates_list, cashflows_list):
	add_transactions('Real_Estate_Investments', dates_list, cashflows_list)
	add_transactions('Real_Estate_Incomes', dates_list, cashflows_list)
	add_bal('Real_Estate_Current_Balance', dates_list, cashflows_list)
	
def include_emergency_fd(dates_list, cashflows_list):
	add_transactions('Emergency_FD_Investments', dates_list, cashflows_list)
	add_transactions('Emergency_FD_Incomes', dates_list, cashflows_list)
	add_bal('Emergency_FD_Principal_Balance', dates_list, cashflows_list)

def include_gold_bar(dates_list, cashflows_list):
	add_transactions('Gold_Investments', dates_list, cashflows_list)
	add_transactions('Gold_Incomes', dates_list, cashflows_list)
	add_bal('Gold_Current_Balance', dates_list, cashflows_list)



def caller(func, message):
	dates_list = []
	cashflows_list = []
	func(dates_list, cashflows_list)
	dates.extend(dates_list)
	cashflows.extend(cashflows_list)
	if len(message) != 0:
		print(width_spacer.format(message) + ' : ' + str(round(xirr(dates_list, cashflows_list)*100, 2)) + " %")


queries = {
	'Kuvera_MFs_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n"  Assets:MFs | sed -e "s/ INR//g"',
	'Kuvera_MFs_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:MF:Kuvera | sed -e \'s/ INR//g\'',
	'Kuvera_MFs_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" --invert -V --depth 2 bal assets:mfs',

	'INDMoney_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg -X INR --cost --format "%d\t%(t) \n"  Assets:INDMoney:ETF | sed -e "s/ INR//g"',
	'INDMoney_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg -X INR --format "%d\t%(amount) \n" Income:PnL:INDMoney | sed -e \'s/ INR//g\'',
	'INDMoney_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" -X INR --invert -V --depth 2 bal Assets:INDMoney:ETF',

	'NPS_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n"  Assets:NPS | sed -e "s/ INR//g"',
	'NPS_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:NPS | sed -e \'s/ INR//g\'',
	'NPS_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" --invert -V --depth 2 bal Assets:NPS',
	
	'EPF_Deposits' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n"  Assets:PF$ | sed -e "s/ INR//g"',
	'EPF_Interest' : 'ledger -f ' + main_ledger_file + ' reg --invert --cost --format "%d\t%(t) \n"  Assets:PF:Interest$ | sed -e "s/ INR//g"',
	'EPF_Net_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:PF$',

	'PPF_Deposits' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n"  Assets:Sbi:PPF$ | sed -e "s/ INR//g"',
	'PPF_Interest' : 'ledger -f ' + main_ledger_file + ' reg --invert --cost --format "%d\t%(t) \n"  Assets:Sbi:PPF:Interest$ | sed -e "s/ INR//g"',
	'PPF_Net_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:Sbi:PPF$',

	'Zerodha_Shares_Gains' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:Stocks:Zerodha | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Dividends' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:Dividends | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n" Assets:Zerodha:Kite | sed -e \'s/ INR//g\'',
	'Zerodha_prev_fy_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2023/09/01" reg --cost --format "%d\t%(t) \n" HDFCBANK IDFCFIRSTB KOTAKBANK SBICARD | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Current_Balance' : 'ledger -f ' + main_ledger_file + ' --invert -V --depth 2 bal Assets:Zerodha:Kite',

	'Real_Estate_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/03/01" reg --cost --format "%d\t%(t) \n" Assets:Plot | sed -e \'s/ INR//g\'',
	'Real_Estate_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:Plot | sed -e \'s/ INR//g\'',
	'Real_Estate_Current_Balance' : 'ledger -f ' + main_ledger_file + ' --invert -V --depth 2 bal Assets:Plot',
	
	'Emergency_FD_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/03/01" reg --cost --format "%d\t%(t) \n" Assets:Sejal:FD | sed -e \'s/ INR//g\'',
	'Emergency_FD_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:Interest:FD$ | sed -e \'s/ INR//g\'',
	'Emergency_FD_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:Sejal:FD',
	
	'Gold_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n"  Assets:Gold:Bar | sed -e "s/ INR//g"',
	'Gold_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:Gold | sed -e \'s/ INR//g\'',
	'Gold_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" --invert -V --depth 2 bal Assets:Gold:Bar',
	
}


# This starts from 01st April, 2024 along with a few shares from the past.
# I have not included private equity in any other calculations so they will be excluded here as well
# Insurance gains will not be included
# Chinku's cash will not be included along with any interest income from savings accounts, etc

caller(include_kuvera_mf, 'Kuvera MFs')
caller(include_nps, 'NPS')
caller(include_Zerodha_Shares, 'Zerodha Shares')
# caller(include_indmoney_etfs, 'INDMoney ETFs')
# caller(include_PPF, 'PPF')
# caller(include_EPF, 'EPF')
# caller(include_emergency_fd, 'FDs')
# caller(include_real_estate, 'Real estate')
# caller(include_gold_bar, 'Gold')

print(width_spacer.format('Overall') + ' : ' + str(round(xirr(dates, cashflows)*100, 2)) + " %")



