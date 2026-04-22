import os
from datetime import datetime

from utils import get_ttm_date, get_ttm_with_curr_date, get_month_range, add_months

configs = {
	'INCEPTION' : {
		'start_date': datetime(2024, 4, 1),
		'end_date': datetime.today(),
	},
	'TTM' : {
		'start_date': max(datetime(2023, 4, 1), get_ttm_date(datetime.today())),
		'end_date': add_months(datetime.today(), 1),
	},
    'REAL_TTM' : {
		'start_date': max(datetime(2023, 4, 1), get_ttm_with_curr_date(datetime.today())),
		'end_date': add_months(datetime.today(), 1),
	},
	'TEST' : {
		'start_date': datetime(2023, 4, 1),
		'end_date': datetime(2024, 3, 1),
	},
}

main_ledger_file = os.environ['LEDGER_MAIN_FILE']
benchmark_ledger_file = os.environ['LEDGER_ROOT']+'/entries/comparison_entries/benchmark-sip.ledger'
prices_db = os.environ['LEDGER_ROOT']+'/entries/comparison_entries/index_prices'

if __name__ == '__main__':
	print(configs['REAL_TTM'])
	print(configs['TTM'])
	print(get_month_range(configs['REAL_TTM']['start_date'], configs['REAL_TTM']['end_date']))
	print(get_month_range(configs['TTM']['start_date'], configs['TTM']['end_date']))