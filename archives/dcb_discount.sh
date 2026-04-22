#!/bin/zsh

# CASH_DISCOUNT=$(ledger bal --invert Equity:Cashback:Infinia:Cash$ | sed -e 's/^ *//' | cut -d ' ' -f 1)
INSTANT_DISCOUNT=$(ledger bal --invert Equity:Cashback:Infinia:Discount$ | sed -e 's/^ *//' | cut -d ' ' -f 1)
RP_BAL=$(ledger bal Equity:Infinia:Reward-Points$ | sed -e 's/^ *//' | cut -d ' ' -f 1)
RP_USED=$(ledger bal --invert Equity:Infinia:Reward-Points:Used$ | sed -e 's/^ *//' | cut -d ' ' -f 1)
DISCOUNT_TO_OTHERS=$(ledger bal Equity:Infinia:Discount:Others$ | sed -e 's/^ *//' | cut -d ' ' -f 1)
TXN_TOTAL=$(ledger bal --invert Liabilities:CreditCard:Infinia$ | sed -e 's/^ *//' | cut -d ' ' -f 1)

# if [ -z $CASH_DISCOUNT ];
# 	then CASH_DISCOUNT=0
# fi

if [ -z $INSTANT_DISCOUNT ];
	then INSTANT_DISCOUNT=0
fi

if [ -z $DISCOUNT_TO_OTHERS ];
	then DISCOUNT_TO_OTHERS=0
fi


# echo 'CASH_DISCOUNT : '$CASH_DISCOUNT
echo 'INSTANT_DISCOUNT : '$INSTANT_DISCOUNT
echo 'RP_BAL : '$RP_BAL
echo 'RP_USED : '$RP_USED
echo 'DISCOUNT_TO_OTHERS : '$DISCOUNT_TO_OTHERS
echo 'TXN_TOTAL : '$TXN_TOTAL

echo ''
echo ''

PERCENT=$(echo '('$RP_BAL'-'$RP_USED')*10000/('$TXN_TOTAL'+'$DISCOUNT_TO_OTHERS')' | bc)
echo 'Unrealised discount : '${PERCENT: : -2}'.'${PERCENT: -2}'%'

PERCENT=$(echo '('$RP_USED'+'$INSTANT_DISCOUNT')*10000/('$TXN_TOTAL'+'$DISCOUNT_TO_OTHERS')' | bc)
echo 'Realised discount : '${PERCENT: : -2}'.'${PERCENT: -2}'%'



