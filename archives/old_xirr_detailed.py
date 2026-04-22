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
	add_transactions('Kuvera_save_smart', dates_list, cashflows_list)
	add_transactions('Kuvera_MFs_Incomes', dates_list, cashflows_list)
	add_bal('Kuvera_MFs_Current_Balance', dates_list, cashflows_list)

def include_EPF(dates_list, cashflows_list):
	add_transactions('EPF_Deposits', dates_list, cashflows_list)
	add_transactions('EPF_Interest', dates_list, cashflows_list)
	add_bal('EPF_Net_Principal_Balance', dates_list, cashflows_list)

def include_PPF(dates_list, cashflows_list):
	add_transactions('PPF_Deposits', dates_list, cashflows_list)
	add_transactions('PPF_Interest', dates_list, cashflows_list)
	add_bal('PPF_Net_Principal_Balance', dates_list, cashflows_list)

def include_Hedonova(dates_list, cashflows_list):
	add_transactions('Hedonova_Investments', dates_list, cashflows_list)
	add_transactions('Hedonova_Incomes', dates_list, cashflows_list)

def include_Zerodha_Shares(dates_list, cashflows_list):
	add_transactions('Zerodha_Shares_Investments', dates_list, cashflows_list)
	add_transactions('Zerodha_Shares_Gains', dates_list, cashflows_list)
	add_transactions('Zerodha_Shares_Dividends', dates_list, cashflows_list)
	add_bal('Zerodha_Shares_Current_Balance', dates_list, cashflows_list)

def include_Zerodha_Mfs(dates_list, cashflows_list):
	add_transactions('Zerodha_MFs_Investments', dates_list, cashflows_list)
	add_transactions('Zerodha_MFs_Incomes', dates_list, cashflows_list)

def include_Sbi_MFs(dates_list, cashflows_list):
	add_transactions('SBIMFs_Investments', dates_list, cashflows_list)
	add_transactions('SBIMFs_Incomes', dates_list, cashflows_list)
	add_bal('SBIMFs_Current_Balance', dates_list, cashflows_list)

def include_SBI_FDs(dates_list, cashflows_list):
	add_transactions('SBI_FD_Investments', dates_list, cashflows_list)
	add_transactions('SBI_FD_Incomes', dates_list, cashflows_list)
	add_bal('SBI_FD_Principal_Balance', dates_list, cashflows_list)

def include_P2P_Lenden(dates_list, cashflows_list):
	add_transactions('P2P_Lenden_Investments', dates_list, cashflows_list)
	add_transactions('P2P_Lenden_Incomes', dates_list, cashflows_list)

def include_Growpital(dates_list, cashflows_list):
	add_transactions('Growpital_Investments', dates_list, cashflows_list)
	add_transactions('Growpital_Incomes', dates_list, cashflows_list)
	add_bal('Growpital_Principal_Balance', dates_list, cashflows_list)

def include_Vcats_PE(dates_list, cashflows_list):
	add_transactions('VCATS_PE_Investments', dates_list, cashflows_list)
	add_transactions('VCATS_PE_Incomes', dates_list, cashflows_list)
	add_bal('VCATS_PE_Current_Balance', dates_list, cashflows_list)

def include_expenses(dates_list, cashflows_list):
	add_transactions('VCATS_PE_Expenses', dates_list, cashflows_list)
	add_transactions('Zerodha_commission_Expenses', dates_list, cashflows_list)

def include_interests(dates_list, cashflows_list):
	add_transactions('Interest_Incomes', dates_list, cashflows_list)

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
	'Kuvera_save_smart' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n"  Assets:Kuvera:SaveSmart | sed -e "s/ INR//g"',
	'Kuvera_MFs_Incomes' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:MF:Kuvera | sed -e \'s/ INR//g\'',
	'Kuvera_MFs_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" --invert -V --depth 2 bal assets:mfs',
	
	'EPF_Deposits' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n"  Assets:PF$ | sed -e "s/ INR//g"',
	'EPF_Interest' : 'ledger -f ' + main_ledger_file + ' reg --invert --cost --format "%d\t%(t) \n"  Assets:PF:Interest$ | sed -e "s/ INR//g"',
	'EPF_Net_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:PF$',

	'PPF_Deposits' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n"  Assets:Sbi:PPF$ | sed -e "s/ INR//g"',
	'PPF_Interest' : 'ledger -f ' + main_ledger_file + ' reg --invert --cost --format "%d\t%(t) \n"  Assets:Sbi:PPF:Interest$ | sed -e "s/ INR//g"',
	'PPF_Net_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:Sbi:PPF$',

	'Hedonova_Investments' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n"  Assets:Hedonova | sed -e "s/ INR//g"',
	'Hedonova_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:PnL:Hedonova | sed -e \'s/ INR//g\'',
	
	'Zerodha_Shares_Gains' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:PnL:Stocks:Zerodha | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Dividends' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --format "%d\t%(amount) \n" Income:Dividends | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Investments' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" reg --cost --format "%d\t%(t) \n" Assets:Zerodha:Kite | sed -e \'s/ INR//g\'',
	'Zerodha_Shares_Current_Balance' : 'ledger -f ' + main_ledger_file + ' -b "2024/04/01" --invert -V --depth 2 bal Assets:Zerodha:Kite',
	
	'Zerodha_MFs_Investments' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Assets:Zerodha:Coin | sed -e \'s/ INR//g\'',
	'Zerodha_MFs_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:PnL:MF:Zerodha | sed -e \'s/ INR//g\'',
	
	'SBIMFs_Investments' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Assets:SBIMF | sed -e \'s/ INR//g\'',
	'SBIMFs_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:PnL:MF:SBI | sed -e \'s/ INR//g\'',
	'SBIMFs_Current_Balance' : 'ledger -f ' + main_ledger_file + ' --invert -V --depth 2 bal Assets:SBIMF',
	
	'SBI_FD_Investments' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Assets:Sbi:FD | sed -e \'s/ INR//g\'',
	'SBI_FD_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:Sbi:Interest$ | sed -e \'s/ INR//g\'',
	'SBI_FD_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:Sbi:FD',

	'P2P_Lenden_Investments' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Assets:P2P:Lenden | sed -e \'s/ INR//g\'',
	'P2P_Lenden_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:PnL:P2P:Lenden | sed -e \'s/ INR//g\'',

	'Growpital_Investments' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Assets:Growpital$ | sed -e \'s/ INR//g\'',
	'Growpital_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:Interest:Growpital$ | sed -e \'s/ INR//g\'',
	'Growpital_Principal_Balance' : 'ledger -f ' + main_ledger_file + ' --invert bal Assets:Growpital$',

	'VCATS_PE_Investments' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Assets:PE | sed -e \'s/ INR//g\'',
	'VCATS_PE_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --format "%d\t%(amount) \n" Income:PnL:PE | sed -e \'s/ INR//g\'',
	'VCATS_PE_Current_Balance' : 'ledger -f ' + main_ledger_file + ' --invert -V --depth 2 bal Assets:PE',

	'VCATS_PE_Expenses' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Expenses:VCATS:Fees | sed -e \'s/ INR//g\'',
	'Zerodha_commission_Expenses' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Expenses:Zerodha:Commission | sed -e \'s/ INR//g\'',
	'Interest_Incomes' : 'ledger -f ' + main_ledger_file + ' reg --cost --format "%d\t%(t) \n" Income:Interest | sed -e \'s/ INR//g\'',
}




# Not included in these calculations are 
# 	1. savings account interest earned
# 	2. Income from insurance like sbilife
# 	3. IPOs for radio city and sbilife
# 	4. House investment
# 	5. Cash given to Chinku

caller(include_kuvera_mf, 'Kuvera MFs')
caller(include_Zerodha_Shares, 'Zerodha Shares')
caller(include_PPF, 'PPF')
caller(include_EPF, 'EPF')
caller(include_expenses, '')
caller(include_interests, '')
# caller(include_Growpital, 'Growpital')
# caller(include_Vcats_PE, 'Startups')
# caller(include_Sbi_MFs, '')
# caller(include_SBI_FDs, '')
# caller(include_Hedonova, '')
# caller(include_Zerodha_Mfs, '')
# caller(include_P2P_Lenden, '')

print(width_spacer.format('Overall') + ' : ' + str(round(xirr(dates, cashflows)*100, 2)) + " %")



