import os
import sys
from datetime import datetime, timedelta
import subprocess


def parse_lot_rows(lot_rows):
	price_unit_date_map = {}
	for row in lot_rows:
		if len(row) == 0:
			continue
		row_parts = row.split('\t')
		date = datetime.strptime(row_parts[0].strip(), '%y-%b-%d')
		units_price_parts = row_parts[1].split(' ', 1)
		units = float(units_price_parts[0].strip())
		lot_price = units_price_parts[1].strip()
		# lots of edge cases to handle here
		if(lot_price in price_unit_date_map):
			if(units < 0):
				final_units = price_unit_date_map[lot_price][0][1] + units
				if(final_units == 0):
					price_unit_date_map[lot_price] = price_unit_date_map[lot_price][1:]
				else:
					price_unit_date_map[lot_price][0][1] = final_units
			else:
				price_unit_date_map[lot_price].append([date, units])
		else:
			price_unit_date_map[lot_price] = [[date, units]]

	return price_unit_date_map


def sort_lots_dict(price_unit_date_map):
	date_lot_list = []
	for price in price_unit_date_map:
		for i in range(0, len(price_unit_date_map[price])):
			date_lot_list.append([price_unit_date_map[price][i][0], str(format(price_unit_date_map[price][i][1], '.3f')) + ' ' + price])

	date_lot_list.sort(key=lambda row: row[0])
	return list(map(lambda lot: datetime.strftime(lot[0], '%y-%b-%d') + '\t' + lot[1], date_lot_list))



account = sys.argv[1]
LOTS_REGISTER_REPORT = subprocess.Popen('tab=$(printf \'\t\'); ledger -f ${LEDGER_MAIN_FILE} reg --format "%d\t%(amount)\n" ' + account + ' | sort -t "$tab" -n -k1.1,1.2 -k1.4,1.6M -k1.8,1.9', shell=True, stdout=subprocess.PIPE).communicate()[0]

lot_rows = LOTS_REGISTER_REPORT.decode('utf-8').split('\n')
price_unit_date_map = parse_lot_rows(lot_rows)
final_sorted_lots = sort_lots_dict(price_unit_date_map)
print("\n".join(final_sorted_lots))



