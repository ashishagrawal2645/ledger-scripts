import os
import re
import subprocess
import tabulate

tabulate.PRESERVE_WHITESPACE = True

# Define colors to be used for positive and negative amounts
RED ='\033[31m'
BLUE ='\033[34m'
NC ='\033[0m'

accounts_list = [
	# 'Assets:Pluxee',
	# 'Assets:Phonepe',
	'Liabilities:CreditCard:Infinia',
	'Liabilities:CreditCard:BizBlack',
	'Liabilities:CreditCard:Premier',
	'Liabilities:CreditCard:EPM',
	'Liabilities:CreditCard:Amex:Platinum',
	'Liabilities:CreditCard:ICICI',
	'Assets:Wallet',
	'Axis:Account',
	'ICICI:Account',
	'HSBC:Account',
	'IDFC:Account',
	'HDFC:Account',
	'Amazon-Shopping$',
	'AmazonPay$',
	'AmazonPay:Wallet$',
	'Assets:Swiggy$',
]
accounts_str = ' '.join(accounts_list)

# only exception to this method is "0  Assets" line
def colorize(line):
	if " " not in line:
		return line

	pieces = list(filter(lambda s: s != '', line.split(" ")))

	if len(pieces) == 3:
		last_space_index = line.rindex(" ")
	else:
		last_space_index = len(line)

	colored_line = line[0:last_space_index]

	if re.match(r'\s+-\d', line):
		colored_line = RED + line[0:last_space_index] + NC

	colored_line = colored_line + BLUE + line[last_space_index:] + NC

	return colored_line

def get_budget():
	HDFC_BUDGET = subprocess.Popen('ledger bal ' + accounts_str, shell=True, stdout=subprocess.PIPE)

	budgets = [HDFC_BUDGET.communicate()[0]]
	budgets = list(map(parse_budget_string, budgets))
	return budgets

# converts stringified budget to list and removes the last entry of empty string
def parse_budget_string(budget):
	cleaned_budget = list(filter(remove_some_accounts, budget.decode('utf-8').split("\n")[:-1]))
	fix_amazon_pay(cleaned_budget)
	return cleaned_budget

def remove_some_accounts(line):
	if ('Others' in line) or ('Repayment' in line):
		return False
	else:
		return True

def fix_amazon_pay(budget):
	index = 0
	for i in range(len(budget)):
		if "AmazonPay" in budget[i]:
			index = i
			break
	amount_to_subtract = get_amount(budget[index+1])
	total_amount = get_amount(budget[index])
	final_amount = total_amount - amount_to_subtract
	len_total_amount = len(str(total_amount))
	len_final_amount = len(str(final_amount))
	str_to_replace = " "*(len_total_amount-len_final_amount)+str(final_amount)
	budget[index] = budget[index].replace(str(total_amount), str_to_replace)

def get_amount(line):
	amount = int(line.split(".00 INR ")[0].strip())
	return amount

def get_aligned_headers():
	account_lengths = max_size_of_text_per_account(budgets)
	aligned_headers = []

	for i in range(0, len(headers)):
		hlen = len(headers[i])
		aligned_headers.append((' ' * int((account_lengths[i] - hlen)/2)) + headers[i])
	return aligned_headers

def max_size_of_text_per_account(budgets):
	return list(map(lambda budget: max(list(map(len,budget))),budgets))

def join_accounts_into_rows(budgets):
	budget_table = []
	max_row_length = max_num_of_rows(budgets)
	for x in range(0,max_row_length):
		table = []
		for y in range(0,len(budgets)):
			if x<len(budgets[y]):
				table.append(colorize(budgets[y][x]))
			else:
				table.append(NC+''+NC)
		budget_table.append(table)
	return budget_table

def max_num_of_rows(budgets):
	return max(list(map(len, budgets)))

def print_table(table, headers):
	print(tabulate.tabulate(table, headers, tablefmt='rst'))


headers=["Balance Report"]

budgets = get_budget()
headers = get_aligned_headers()
table = join_accounts_into_rows(budgets)
print_table(table, headers)
