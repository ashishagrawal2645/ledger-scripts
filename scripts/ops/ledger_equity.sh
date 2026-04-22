#!/bin/bash

FISCAL_YEAR=${1}

echo "Please make sure to consolidate virtual transactions before proceed..."
echo "press ctrl+c to quit now"
read -n 1 -p "Press any key to continue:" input

echo "Please make sure to remove include diners-cashback and virtual txns from main file before proceeding..."
echo "press ctrl+c to quit now"
read -n 1 -p "Press any key to continue:" input

echo "Creating new directory for ledger files : "$FISCAL_YEAR
mkdir -p $LEDGER_ROOT/entries/$FISCAL_YEAR

echo "Generating new ledger file with equity for all the ledger files specified"
ledger -f ${LEDGER_MAIN_FILE} -e "$FISCAL_YEAR/04/01" --real --lots equity > /tmp/journal-equity.ledger

echo "Moving files to respective direcories.."
mv /tmp/journal-equity.ledger $LEDGER_ROOT/entries/$FISCAL_YEAR/equity.ledger

echo "Adding new ledger files to main ledger file"
echo "" >> $LEDGER_ROOT/entries/main.ledger
echo "" >> $LEDGER_ROOT/entries/main.termux.ledger
echo "" >> $LEDGER_ROOT/entries/main.mac.ledger
echo "" >> $LEDGER_ROOT/entries/main.ci.ledger

echo "include $FISCAL_YEAR/data.ledger" >> $LEDGER_ROOT/entries/main.ledger
echo "include $FISCAL_YEAR/data.ledger" >> $LEDGER_ROOT/entries/main.termux.ledger
echo "include $FISCAL_YEAR/data.ledger" >> $LEDGER_ROOT/entries/main.mac.ledger
echo "include $FISCAL_YEAR/data.ledger" >> $LEDGER_ROOT/entries/main.ci.ledger


echo "" >> $LEDGER_ROOT/configs/ledger-files.conf
echo "$FISCAL_YEAR" >> $LEDGER_ROOT/configs/ledger-files.conf

echo "All files updated...."
echo "update current.ledger to update the new directories equity and data ledgers"
echo "update date in equity file to $FISCAL_YEAR/03/31"

