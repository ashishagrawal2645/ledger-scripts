import argparse
import tabulate

tabulate.PRESERVE_WHITESPACE = True

def print_table(table, headers, label):
    if len(label) != 0:
        print("")
        print(label)
    print(tabulate.tabulate(table, headers, tablefmt='rounded_grid', floatfmt=".2f"))


headers = ["Command", "Description"]
operations = [
	# Operations
    ["fava-ledger",                       "Runs fava with current ledger files in a UI"],
	["fava-accounts",                     "Generates account list"],
]

others = [
    # Others
    ["liabilities",                       "Get only liabilities for an account"],
	["lots_balances",                     "Get balances with lots for each commodity"],
	["fire --yearly",                     "Gets the yearly percentage of expenses that was covered from other incomes"],
	["exp --yearly",                      "Shows yearly expenses from FY2017 onwards"],
]

frequently_used = [
    # Frequently used
	["balance-report",                    "Gets balance across all commmonly used accounts"],
	["exp",                               "Shows monthly expenses for the current financial year"],
	["nw",                                "Shows increase in networth year on year, and the overall"],
	["fire",                              "Gets the monthly percentage of expenses that can be covered from other incomes"],
]

investment = [
    # Investment aliases
	["xirr",                              "Shows current xirr of each asset class and overall"],
    ["retirement-tracker",                "Compares expectations with reality for my retirement (only considers MFs and PF)"],
	["cost-basis-allocation",             "Asset allocation across asset classes based on amount invested"],
	["mf-performance",                    "Compares my mutual funds performance vs Nifty 50"],
	["mf-growth",                         "Compares current value vs invested for my mutual fund investments"],
	["mf-allocation",                     "Asset allocation across different mutual funds based on current value"],
	["valuation-basis-allocation",        "Asset allocation across asset classes based on current value"],
	["allocation",                        "Shows allocation across all assets as a list"],
]

credit_cards = [
    # Credit card aliases
    ["cc-usage",                          "Shows credit card annual spends, milestones that should be met, and days left"],
	["rewards",                           "Shows reward points balance as of yesterday for all credit cards"],
	["cc-discount",                      "Discount percantage for Infinia for overall spends"],
]


def argumentParser():
    parser = argparse.ArgumentParser(description='Optional app params')

    # Switch
    parser.add_argument('--operations', action='store_true',
                        help='Show commands for operations')
    
    parser.add_argument('--others', action='store_true',
                        help='Show commands for others')
    
    parser.add_argument('--frequently_used', action='store_true',
                        help='Show commands for frequently_used')
    
    parser.add_argument('--investments', action='store_true',
                        help='Show commands for investments')
    
    parser.add_argument('--credit_cards', action='store_true',
                        help='Show commands for credit_cards')
    
    parser.add_argument('--all', action='store_true',
                        help='Show commands for all')

    return parser.parse_args()


if __name__ == '__main__':
    args = argumentParser()

    if args.all:
        print_table(operations, headers, "Operations")
        print_table(others, headers, "Others")
        print_table(frequently_used, headers, "Frequently used")
        print_table(investment, headers, "Investments")
        print_table(credit_cards, headers, "Credit cards")
    else:
        invalid_flag = False
        if args.operations:
            print_table(operations, headers, "")
            invalid_flag = True
        
        if args.others:
            print_table(others, headers, "")
            invalid_flag = True
        
        if args.frequently_used:
            print_table(frequently_used, headers, "")
            invalid_flag = True
        
        if args.investments:
            print_table(investment, headers, "")
            invalid_flag = True
        
        if args.credit_cards:
            print_table(credit_cards, headers, "")
            invalid_flag = True
        
        if invalid_flag == False:
            print("Please select a valid flag")
    
    
    
