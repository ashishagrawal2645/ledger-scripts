import os
import sys
import subprocess
import tabulate
from datetime import date
from dateutil.relativedelta import relativedelta
from babel.numbers import format_currency

sys.path.append(os.environ['LEDGER_REPORTS']+'/investments')
from configs import main_ledger_file

tabulate.PRESERVE_WHITESPACE = True

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_latest_dates(date_config):
    today = date.today()
    
    curr_date = date.today()
    prev_date = date.today()
    next_date = date.today()
    if date_config['type'] == 'yearly':
        date_parts = date_config['period'].split('/')
        curr_date = date(today.year, int(date_parts[1]), int(date_parts[0]))
        prev_date = curr_date - relativedelta(years=1)
        next_date = curr_date + relativedelta(years=1)
    else:
        curr_date = date(today.year, today.month, int(date_config['period']))
        prev_date = curr_date - relativedelta(months=1)
        next_date = curr_date + relativedelta(months=1)
    
    result = {}
    if(curr_date >= today):
        result['start_date'] = prev_date
        result['end_date'] = curr_date
    else:
        result['start_date'] = curr_date
        result['end_date'] = next_date
    return result
    


def days_to_end(end_date):
    today = date.today()
    delta = end_date - today
    return delta.days


def get_spends_for_current_annual_cycle(account, start_date, end_date):
    start_date_str = start_date.strftime('%Y/%m/%d')
    end_date_str = end_date.strftime('%Y/%m/%d')
    command = subprocess.Popen('ledger -f ' + main_ledger_file + ' bal -b "' + start_date_str + '" -e "' + end_date_str + '" --format "%(T) \n" ' + account, shell=True, stdout=subprocess.PIPE)
    output = command.communicate()[0]
    if(len(output) > 0):
        amount = output.decode('utf-8').split("INR")[0]
        return float(amount)
    else:
        return 0


def build_row(card, total, end_date):
    target = configs[card]['target']
    diff = target + total
    diff_str = ''
    if(diff < 0):
        diff_str = bcolors.BOLD + bcolors.OKGREEN + format_currency(diff, 'INR', locale='en_IN').replace(u'\xa0', u' ') + bcolors.ENDC
    else:
        diff_str = bcolors.BOLD + bcolors.FAIL + format_currency(diff, 'INR', locale='en_IN').replace(u'\xa0', u' ') + bcolors.ENDC
    return [
        card,
        format_currency(-1*total, 'INR', locale='en_IN').replace(u'\xa0', u' '),
        format_currency(target, 'INR', locale='en_IN').replace(u'\xa0', u' '),
        days_to_end(end_date),
        diff_str,
    ]


def build_table():
    table = []
    for key in configs:
        dates = get_latest_dates(configs[key]['date_config'])
        total = 0
        for account in configs[key]['accounts']:
            total += get_spends_for_current_annual_cycle(account, dates['start_date'], dates['end_date'])
        
        row = build_row(key, total, dates['end_date'])
        table.append(row)
    return table


def print_table(table, headers):
	print(tabulate.tabulate(table, headers, colalign=col_alignment, tablefmt='rst', floatfmt=".2f"))


configs = {
    "Infinia" : {
        "accounts" : ['Liabilities:CreditCard:Infinia$', 'Liabilities:CreditCard:Infinia:Others$'],
        "date_config" : {
            "type": "yearly",
            "period": '01/04',
        },
        "target": 1000000.00,
    },
    "BizBlack" : {
        "accounts" : ['Liabilities:CreditCard:BizBlack$', 'Liabilities:CreditCard:BizBlack:Others$'],
        "date_config" : {
            "type": "yearly",
            "period": '06/12',
        },
        "target": 750000.00,
    },
    "Amex Platinum" : {
        "accounts" : ['Liabilities:CreditCard:Amex:Platinum$', 'Liabilities:CreditCard:Amex:Platinum:Others$'],
        "date_config" : {
            "type": "yearly",
            "period": '23/09',
        },
        "target": 400000.00,
    },
    "Amex Gold" : {
        "accounts" : ['Liabilities:CreditCard:Amex:Gold$', 'Liabilities:CreditCard:Amex:Gold:Others$'],
        "date_config" : {
            "type": "monthly",
            "period": '01',
        },
        "target": 6000.00,
    },
    "BizBlack Monthly" : {
        "accounts" : ['Liabilities:CreditCard:BizBlack$', 'Liabilities:CreditCard:BizBlack:Others$'],
        "date_config" : {
            "type": "monthly",
            "period": '22',
        },
        "target": 50000.00,
    },
}

col_alignment = ['left', 'right', 'right', 'right', 'right']
headers = ['Card', 'Total spends', 'Target', 'Days left', 'Difference']
table = build_table()
print_table(table, headers)