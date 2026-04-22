#!/bin/bash

echo '990000+'`ledger --real  balance Liabilities:CreditCard:HDFC` | cut -d ' ' -f 1,2 | bc
