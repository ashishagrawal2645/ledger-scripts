import subprocess
import tabulate
from datetime import date
from dateutil.relativedelta import relativedelta

tabulate.PRESERVE_WHITESPACE = True


def get_monthly_date():
    today = date.today()
    curr_date = date(today.year, today.month, 1)
    next_date = curr_date + relativedelta(months=1)
    return (curr_date.strftime('%Y/%m/%d'), next_date.strftime('%Y/%m/%d'))


def get_biz_bonus_date():
    today = date.today()
    curr_date = date(today.year, today.month, 24)
    prev_date = date(today.year, today.month, 24) - relativedelta(months=1)
    next_date = date(today.year, today.month, 24) + relativedelta(months=1)
    if(curr_date >= today):
        return (prev_date.strftime('%Y/%m/%d'), curr_date.strftime('%Y/%m/%d'))
    else:
        return (curr_date.strftime('%Y/%m/%d'), next_date.strftime('%Y/%m/%d'))
    


def get_balance_earned(account):
    begin_date, end_date = get_monthly_date()
    command = subprocess.Popen('ledger bal -b "' + begin_date + '" -e "' + end_date + '" --format "%(T) \n" --limit "account=~/' + account + '/ and payee=~/[2-9]x/"', shell=True, stdout=subprocess.PIPE)
    output = command.communicate()[0]
    if(len(output) > 0):
        amount = output.decode('utf-8').split("INR")[0]
        return float(amount)
    else:
        return 0


def get_biz_balance_earned(account):
    begin_date, end_date = get_biz_bonus_date()
    command = subprocess.Popen('ledger bal -b "' + begin_date + '" -e "' + end_date + '" --format "%(T) \n" --limit "account=~/' + account + '/ and payee=~/[2-9]x biz bonus/"', shell=True, stdout=subprocess.PIPE)
    output = command.communicate()[0]
    if(len(output) > 0):
        amount = output.decode('utf-8').split("INR")[0]
        return float(amount)
    else:
        return 0


def get_balance(account):
    today = date.today().strftime('%Y/%m/%d')
    command = subprocess.Popen('ledger bal -e "' + today + '" --format "%(T) \n" ' + account, shell=True, stdout=subprocess.PIPE)
    output = command.communicate()[0]
    if(len(output) > 0):
        amount = output.decode('utf-8').split("INR")[0]
        return float(amount)
    else:
        return 0


def compute_total_table():
    table = []
    for key in configs:
        limit = configs[key]['smartbuy_limits'] if 'smartbuy_limits' in configs[key] else '-'
        biz_limit = configs[key]['biz_bonus_limits'] if 'biz_bonus_limits' in configs[key] else '-'
        total = 0
        total += get_balance(configs[key]['credits'])
        total += get_balance(configs[key]['debits'])
        if 'smartbuy_limits' in configs[key]:
            earned = get_balance_earned(configs[key]['credits'])
            bonus = get_biz_balance_earned(configs[key]['credits'])
            bonus = '-' if bonus == 0 else bonus
            table.append([key, total, earned, limit, bonus, biz_limit])
        else:
            table.append([key, total, '-', '-', '-', '-'])
    return table


def print_table(table, headers):
	print(tabulate.tabulate(table, headers, colalign=col_alignment, tablefmt='rst', floatfmt=".2f"))


configs = {
    "Infinia" : {
        "credits" : 'Equity:Infinia:Reward-Points$',
        "debits" : 'Equity:Infinia:Reward-Points:Used$',
        "smartbuy_limits" : 15000,
    },
    "BizBlack" : {
        "credits" : 'Equity:BizBlack:Reward-Points$',
        "debits" : 'Equity:BizBlack:Reward-Points:Used$',
        "smartbuy_limits" : 10000,
        "biz_bonus_limits" : 7500,
    },
    "Amex Platinum" : {
        "credits" : 'Equity:Amex:Platinum:Reward-Points$ Equity:Amex:Gold:Reward-Points$',
        "debits" : 'Equity:Amex:Platinum:Reward-Points:Used$ Equity:Amex:Gold:Reward-Points:Used$',
    },
    "HSBC Premier" : {
        "credits" : 'Equity:Premier:Reward-Points$',
        "debits" : 'Equity:Premier:Reward-Points:Used$',
        "smartbuy_limits" : 18000,
    },
    "EPM" : {
        "credits" : 'Equity:EPM:Reward-Points$',
        "debits" : 'Equity:EPM:Reward-Points:Used$',
        "smartbuy_limits" : 18000,
    },
    # "Amex Gold" : {
    #     "credits" : 'Equity:Amex:Gold:Reward-Points$',
    #     "debits" : 'Equity:Amex:Gold:Reward-Points:Used$',
    # },
}

col_alignment = ['left', 'right', 'right', 'right', 'right']
headers = ['Card', 'Rewards balance', 'Smartbuy points', 'Smartbuy Limits', 'Biz Bonus points', 'Biz bonus limits']
table = compute_total_table()
print_table(table, headers)

