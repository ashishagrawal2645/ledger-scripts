import subprocess
import tabulate
from babel.numbers import format_currency

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


def get_balance(account):
    command = subprocess.Popen('ledger bal --format "%(T) \n" ' + account, shell=True, stdout=subprocess.PIPE)
    output = command.communicate()[0]
    if(len(output) > 0):
        amount = output.decode('utf-8').split("INR")[0]
        return float(amount)
    else:
        return 0


def format_row(card, total_spends, realised_gains, unrealised_gains):
    return [
        card,
        format_currency(total_spends, 'INR', locale='en_IN').replace(u'\xa0', u' '),
        "{:.2f}%".format(realised_gains),
        "{:.2f}%".format(unrealised_gains),
    ]


def build_table():
    table = []
    for key in configs:
        total = -1 * get_balance(configs[key]['total'])
        discount_to_others = get_balance(configs[key]['discount_to_others'])
        rp_used = -1 * get_balance(configs[key]['reward_points_used'])
        rp_bal = get_balance(configs[key]['reward_points_balance'])
        cash_discount = -1 * get_balance(configs[key]['cash_discount'])
        total_spends = total+discount_to_others
        unrealised_gains = (rp_bal - rp_used)*configs[key]['multiplier']*100/total_spends
        realised_gains = (rp_used + cash_discount)*100/total_spends
        formatted_row = format_row(key, total_spends, realised_gains, unrealised_gains)
        table.append(formatted_row)
    return table


def print_table(table, headers):
	print(tabulate.tabulate(table, headers, colalign=col_alignment, tablefmt='rst', floatfmt=".2f"))


configs = {
    "Infinia" : {
        "total": "Liabilities:CreditCard:Infinia$",
        "discount_to_others": "Equity:Infinia:Discount:Others$",
        "reward_points_used": "Equity:Infinia:Reward-Points:Used$",
        "reward_points_balance": "Equity:Infinia:Reward-Points$",
        "cash_discount": "Equity:Cashback:Infinia:Discount$",
        "multiplier": 1.0,
    },
    "BizBlack" : {
        "total": "Liabilities:CreditCard:BizBlack$",
        "discount_to_others": "Equity:BizBlack:Discount:Others$",
        "reward_points_used": "Equity:BizBlack:Reward-Points:Used$",
        "reward_points_balance": "Equity:BizBlack:Reward-Points$",
        "cash_discount": "Equity:Cashback:BizBlack:Discount$",
        "multiplier": 1.0,
    },
    "Amex Platinum" : {
        "total": "Liabilities:CreditCard:Amex:Platinum$",
        "discount_to_others": "Equity:Amex:Platinum:Discount:Others$",
        "reward_points_used": "Equity:Amex:Platinum:Reward-Points:Used$",
        "reward_points_balance": "Equity:Amex:Platinum:Reward-Points$",
        "cash_discount": "Equity:Cashback:Amex:Platinum:Discount$",
        "multiplier": 0.5,
    },
    "Amex Gold" : {
        "total": "Liabilities:CreditCard:Amex:Gold$",
        "discount_to_others": "Equity:Amex:Gold:Discount:Others$",
        "reward_points_used": "Equity:Amex:Gold:Reward-Points:Used$",
        "reward_points_balance": "Equity:Amex:Gold:Reward-Points$",
        "cash_discount": "Equity:Cashback:Amex:Gold:Discount$",
        "multiplier": 0.5,
    },
    "Premier" : {
        "total": "Liabilities:CreditCard:Premier$",
        "discount_to_others": "Equity:Premier:Discount:Others$",
        "reward_points_used": "Equity:Premier:Reward-Points:Used$",
        "reward_points_balance": "Equity:Premier:Reward-Points$",
        "cash_discount": "Equity:Cashback:Premier:Discount$",
        "multiplier": 1.0,
    },
}

col_alignment = ['left', 'right', 'right', 'right']
headers = ['Card', 'Total lifetime spends', 'Realised gains', 'Unrealised gains']
table = build_table()
print_table(table, headers)