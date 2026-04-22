import os
import sys
from babel.numbers import format_currency
from datetime import datetime
import argparse

sys.path.append(os.environ['LEDGER_REPORTS']+'/investments')
from configs import configs, main_ledger_file
from utils import MONTHLY_VALUE, TOTAL_VALUE
from utils import get_register_report

import seaborn as sns  # type: ignore
import pandas as pd
import matplotlib.pyplot as plt  # type: ignore

from investments.expectations import expenses

def yearly_reporting():
    report = {}
    total_spends = 0.0
    fiscal_data = get_fiscal_years()

    for (key, value) in fiscal_data.items():
        (data, yearly_expense) = calculate_report(
            value['start_date'], value['end_date'])
        report[key] = yearly_expense
        total_spends = total_spends + yearly_expense
    return (report, total_spends)


def get_fiscal_years():
    fiscal_years = {}
    for year in supported_fiscal_years:
        key = f'FY{str(year)[-2:]}'
        (start_date, end_date) = get_fy_dates(year)
        value = {
            'start_date': start_date,
            'end_date': end_date
        }
        fiscal_years[key] = value
    return fiscal_years


def non_yearly_reporting(args):
    start_date = ''
    end_date = ''
    if args.ttm:
        start_date = configs['TTM']['start_date']
        end_date = configs['TTM']['end_date']
    elif args.real_ttm:
        start_date = configs['REAL_TTM']['start_date']
        end_date = configs['REAL_TTM']['end_date']
    else:
        (start_date, end_date) = get_fy_dates(args.monthly)

    return calculate_report(start_date, end_date)


def get_fy_dates(year):
    format = '%Y/%m/%d'
    start_date = datetime.strptime(f'{year}/04/01', format)
    end_date = datetime.strptime(f'{year+1}/04/01', format)
    return (start_date, end_date)


def calculate_report(start_date, end_date):
    accounts = 'Expenses and not \\(Expenses:Taxes or Expenses:Donation:Political\\)'
    report = get_register_report(ledger_file=main_ledger_file,
                                 accounts=accounts, start_date=start_date, end_date=end_date)
    data = {}
    total_expenses = 0
    for (key, value) in report.items():
        data[key] = human_readable(value[MONTHLY_VALUE])
        total_expenses = max(total_expenses, value[TOTAL_VALUE])
    total_expenses = human_readable(total_expenses)
    return (data, total_expenses)


def human_readable(num):
    return round(num/100000, 2)

def getExpectedExpenses(keys):
    total = 0
    for item in keys:
        total += expenses[item][0]
    return total


def plot_graph(fiscal_months, xAxis_label, results):
    data = pd.DataFrame({
        xAxis_label: [key for key in fiscal_months],
        "Spend (in Lacs)": [float(results[key]) for key in fiscal_months],
    })

    ax = sns.barplot(data=data, 
                     palette="husl", hue=xAxis_label, legend=False, 
                     x=xAxis_label, y="Spend (in Lacs)")
    for i in ax.containers:
        ax.bar_label(i, color='white', size=9)

    ax.xaxis.label.set_color('yellow')
    ax.tick_params(axis='x', colors='yellow', labelrotation=45)

    ax.yaxis.label.set_color('yellow')
    ax.tick_params(axis='y', colors='yellow')
    # ax.ticklabel_format(style='plain', axis='y',useOffset=False)

    plt.savefig("/tmp/expenses-progression.png", dpi=300, transparent=True)
    os.system("~/.iterm2/imgcat -W 95% -H 95% /tmp/expenses-progression.png")


def argumentParser():
    parser = argparse.ArgumentParser(description='Optional app params')

    # Switch
    parser.add_argument('--yearly', action='store_true',
                        help='run execution for fiscal years')

    parser.add_argument('--monthly', type=int, choices=supported_fiscal_years,
                        default=supported_fiscal_years[-1], help='run execution monthly for fiscal years')

    parser.add_argument('--ttm', action='store_true',
                        help='run for trailing twelve months')

    parser.add_argument('--real_ttm', action='store_true',
                        help='run for trailing twelve months including current month')

    return parser.parse_args()


supported_fiscal_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

if __name__ == '__main__':
    args = argumentParser()
    xAxis = ''
    if args.yearly:
        (report, total_expenses) = yearly_reporting()
        xAxis = "Years"
        expected_expenses = None
    else:
        (report, total_expenses) = non_yearly_reporting(args)
        expected_expenses = getExpectedExpenses(report.keys())/100000
        xAxis = "Months"

    plot_graph(report.keys(), xAxis, report)
    
    if expected_expenses:
        print("Overall : " + format_currency(total_expenses, 'INR', locale='en_IN') + " lacs, " + 
          "Expected : " + format_currency(expected_expenses, 'INR', locale='en_IN') + " lacs")
    else:
        print("Overall : " + format_currency(total_expenses, 'INR', locale='en_IN') + " lacs")
    # print("Expense ratio : " + str(round(totals*100/income_totals,2)) + "%")
