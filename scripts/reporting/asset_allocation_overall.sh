#!/bin/bash

export total=`ledger -f $LEDGER_MAIN_FILE bal -X INR --depth 1 assets --format "%(quantity(market(display_total)))"`
ledger -f $LEDGER_MAIN_FILE bal -B -S "-abs(T)" -X INR --depth 2 assets --format "%-17((depth_spacer)+(partial_account)) %10(percent(market(display_total), ${total})) %16(market(display_total))\n%/"
