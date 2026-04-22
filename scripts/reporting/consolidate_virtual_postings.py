from datetime import datetime, timedelta
import os
import re
import sys
import subprocess


def format_txn(txn):
	rindex = txn.rindex(" ")
	spaces_to_append = 72 - rindex - 2
	if spaces_to_append == 0:
		pass
	elif spaces_to_append > 0:
		txn = txn[0:txn.rindex(']')+1] + " " * spaces_to_append + txn[txn.rindex(']')+1:]
	return txn


virtual_ledger = os.environ['LEDGER_ROOT'] + "/entries/common/virtual.ledger"
budget_ledger = os.environ['LEDGER_ROOT'] + "/entries/common/budget.ledger"
data_ledger = os.environ['LEDGER_CURRENT_DATA']
include_budget_text = "include ../common/budget.ledger"


date = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime("%Y/%m/%d")
yesterday = (datetime.strptime(date, "%Y/%m/%d") - timedelta(days=1)).strftime("%Y/%m/%d")
equity = subprocess.Popen('ledger equity -e "' + date + '"', shell=True, stdout=subprocess.PIPE).communicate()[0]
equity = equity.decode('utf-8').split('\n')

# Change opening balance to closing balance
desc = yesterday + " Closing balances\n"

# remove all non-virtual transactions
virtual_txns = list(map(lambda txn: format_txn(txn), filter(lambda txn: re.match(r'\s+\[.*\]', txn), equity[1:])))

with open(virtual_ledger, "w") as file: 
	file.write(desc + "\n".join(virtual_txns) + "\n\n") 

data = []
with open(data_ledger, "r") as file:
	data = file.readlines()
	data = filter(lambda txn: include_budget_text not in txn, data)
	appendedData = []
	include_added = False
	for txn in data:
		if (date in txn) and not include_added:
			appendedData.append(include_budget_text)
			appendedData.append("\n\n")
			include_added = True
		appendedData.append(txn)
	if not include_added:
		appendedData.append("\n\n")
		appendedData.append(include_budget_text)
		appendedData.append("\n\n")
	data = appendedData


with open(data_ledger, "w") as file:
	file.writelines(data)

with open(budget_ledger, "r") as file:
	data = file.readlines()
	start_date = list(filter(lambda txn: "start_date" in txn, data))[0].split("=")[1].strip()
	data = map(lambda txn: txn.replace(start_date, date), data)

with open(budget_ledger, "w") as file:
	file.writelines(data)


