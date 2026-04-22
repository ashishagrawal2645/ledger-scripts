# year beginning asset valuation using current prices
ledger -f entries/main.mac.ledger --yearly --empty --collapse -V --price-db scripts/db/prices.db -b "2018/01/01" reg Assets:Chinku:Investment Assets:EPS Assets:Golu:Investment Assets:Growpital Assets:HDFC:FD Assets:Hedonova Assets:Kuvera:Account Assets:Kuvera:SaveSmart Assets:MFs Assets:P2P:Lenden Assets:PE Assets:PF Assets:SBIMF Assets:Sbi:FD Assets:Sbi:PPF Assets:Sbi:RD Assets:Zerodha

# yearly income from Jan-Dec
ledger -f entries/main.mac.ledger --yearly --empty --collapse -b "2018/01/01" reg Income

# Net worth at end date
ledger -f entries/main.mac.ledger -e "2018/04/01" bal -V --depth 1 Assets Liabilities

# monthly expenses sorted by amount, excluding taxes
ledger -f entries/main.mac.ledger -b "2022/09/01" -M -S amount reg expenses and not \(Expenses:Taxes:IncomeTax or Expenses:Taxes:Professional-Tax or Expenses:Donation:Political\)

# asset allocation separated by tabs and formatted
ledger -f $LEDGER_MAIN_FILE bal -V -S -display_total --depth 2 assets --format "%-17((depth_spacer)+(partial_account)) %10(percent(market(display_total), market(parent.total))) %16(market(display_total))\n%/"

# Asset during a period reporting only amount
ledger -f entries/main.mac.ledger -b "2022/04/01" -e "2023/04/01" bal -V --format "%(T) \n" --depth 1 Assets

# only shows for depth = 1
ledger -f $LEDGER_MAIN_FILE bal -B -b "2018/04/01" -e "2019/04/01" --no-total -n Income:Dividends Income:House1 Income:Interest

# Shows yearly passive income
ledger-main --yearly --depth 1 reg Income: and not \(Arcesium Cleartax UrbanClap\)



ledger -f entries/main.mac.ledger -b "2022/04/01" -e "2023/04/01" -M --limit "amount>5000" --depth 2 reg expenses and not \(Expenses:Taxes:IncomeTax or Expenses:Taxes:Professional-Tax or Expenses:Donation:Political\)

ledger -f entries/main.mac.ledger -b "2022/04/01" -e "2023/04/01" bal Equity:Diners:Reward-Points:Used Expenses:Travel


ledger -f entries/main.mac.ledger -b "2018/04/01" -e "2024/04/01" --yearly --limit "amount>5000" --depth 2 reg expenses and not \(Expenses:Taxes:IncomeTax or Expenses:Taxes:Professional-Tax or Expenses:Donation:Political\)

# reg command with custom format and cost-basis values
ledger -B -X INR reg Assets:MFs -b "2025-05-01" --format "%(format_date(date, '%Y-%m-%d'))####%(account)####%(scrub(display_amount))\n"

# monthly investment and total valuation at market value with ajustment posting to show gains month over month using prices db
ledger -f data.ledger -M -V  --no-revalued --price-db prices reg mf

# asset allocation in my MFs
ledger -f data.ledger bal -V -S -display_total --price-db prices --depth 3 assets:MF assets:Index --format "%-17((depth_spacer)+(partial_account)) %10(percent(market(display_total), market(parent.total))) %16(market(display_total))\n%/"


# average buy price of NIFTY in the last 12 months
ledger -f $LEDGER_ROOT/entries/comparison_entries/benchmark-sip.ledger --begin "12 months ago"  --average-lot-prices bal Benchmark

# Logic to calculate gains from Arun
/*
    - filter all transactions from arun-bhaiya
    - get balance of all used points
    - get balance of discounts given
    - divide the discount given to used points
    - (1 - that) gives me the conversion percentage of reward points to cash
    - all reward points gained from arun's booking are extra
    - it will converge to 90% for value but that also happens when I use the points as well
    - So this is the optimal strategy
*/