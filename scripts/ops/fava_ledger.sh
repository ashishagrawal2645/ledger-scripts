#!/bin/bash

LEDGER_ENTRIES=${LEDGER_ROOT}/entries
LEDGER_CONFIGS=${LEDGER_ROOT}/configs
LEDGER_FOLDERS=${LEDGER_CONFIGS}/ledger-files.conf
L2B_CONFIG=${LEDGER_ROOT}/configs/ledger2beancount.${LEDGER_CONFIG_PREFIX}yml
# TMPDIR="${TMPDIR:-/tmp}"

TMPDIR=/tmp

L2B=${LEDGER_ROOT}/ledger2beancount/bin/ledger2beancount

# Killing previous servers
echo "Killing previous servers...."
pkill -f "fava ${TMPDIR}/main.beancount"

# Killing all previous watches
echo "Killing previous watches...."
pkill -f 'entr -p -s ledger'


# Converting all ledger files to beancount in folders present in ledger-files.conf
while IFS="" read -r FISCAL_YEAR || [ -n "$FISCAL_YEAR" ]
do
	mkdir -p $TMPDIR/$FISCAL_YEAR

	echo "Starting file conversion and watchers for entries in "$FISCAL_YEAR"...."

	for x in $LEDGER_ENTRIES/$FISCAL_YEAR/*.ledger; do
		FILE=$(echo $x | sed -re "s|$LEDGER_ENTRIES/$FISCAL_YEAR/||" -re "s|([[:alpha:]])\.ledger$|\1|"); 

		ORIGINAL_FILE=$LEDGER_ENTRIES/$FISCAL_YEAR/$FILE.ledger
		CONVERTED_FILE=$TMPDIR/$FISCAL_YEAR/$FILE.beancount

		original_file_time=$(date -r "$ORIGINAL_FILE" +%s)
		converted_file_time=$(date -r "$CONVERTED_FILE" +%s)

		if (( original_file_time >= converted_file_time )); then
			${L2B} $ORIGINAL_FILE --config ${L2B_CONFIG} > $CONVERTED_FILE
		fi
		(ls $ORIGINAL_FILE | entr -p -s "ledger print --generated -f $ORIGINAL_FILE | ${L2B} --config ${L2B_CONFIG} > $CONVERTED_FILE" > /dev/null 2>&1 &)
	done

done < $LEDGER_FOLDERS

# Converting main ledger file
${L2B} ${LEDGER_MAIN_FILE} --config ${L2B_CONFIG} > ${TMPDIR}/main.beancount
(ls ${LEDGER_MAIN_FILE} | entr -p -s "${L2B} ${LEDGER_MAIN_FILE} --config ${L2B_CONFIG} > ${TMPDIR}/main.beancount" > /dev/null 2>&1 &)

echo "Starting fava server...."
fava $TMPDIR/main.beancount &

