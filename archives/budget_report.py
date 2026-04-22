import os
import re
import subprocess
import tabulate

tabulate.PRESERVE_WHITESPACE = True

# Define colors to be used for positive and negative amounts
RED ='\033[31m'
BLUE ='\033[34m'
NC ='\033[0m'

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
	AXIS_BUDGET = subprocess.Popen('ledger bal --limit "account =~ /budget|axis/" Bonus CreditCard:AMEX CreditCard:HDFC CreditCard:IDFC Investments:Retirement Insurance:ICICI-Term Rent:Flat Household Food-Dining Trip Travel Rent:Housekeeping Entertainment Transport Medical Books Gifts Shopping Sports-Fitness House1:Expenses PersonalCare Bike:Servicing Rent:Muncipality Bills Krishna Unbudgeted Account', shell=True, stdout=subprocess.PIPE)
	HDFC_BUDGET = subprocess.Popen('ledger bal Sbi:Account IDFC:Account HDFC:Account HDFC:Atharv', shell=True, stdout=subprocess.PIPE)
    # HDFC_BUDGET = subprocess.Popen('ledger bal --limit "account =~ /budget|hdfc/" Loan:Personal-Loan$ Loan:House1 Loan:Home-loan-Top-Up Account', shell=True, stdout=subprocess.PIPE)
	# SBI_BUDGET = subprocess.Popen('ledger bal --no-total --flat Sbi:Account IDFC:Account', shell=True, stdout=subprocess.PIPE)

	budgets = [AXIS_BUDGET.communicate()[0], HDFC_BUDGET.communicate()[0]]
	budgets = list(map(parse_budget_string, budgets))
	return budgets

# converts stringified budget to list and removes the last entry of empty string
def parse_budget_string(budget):
	return budget.decode('utf-8').split("\n")[:-1]

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


headers=["Axis Account", "HDFC/IDFC/Sbi Account"]

budgets = get_budget()
headers = get_aligned_headers()
table = join_accounts_into_rows(budgets)
print_table(table, headers)
