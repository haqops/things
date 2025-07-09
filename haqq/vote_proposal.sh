#!/bin/bash

VAL_NAME=
PROPOSAL_ID=
VOTE=yes

HAQQD_BIN=~/bin/haqqd
RPC_URL=https://rpc.tm.haqq.network:443
GAS_ADJUSTMENT=1.7
CHAIN_ID=haqq_11235-1
GAS_PRICES=27500000000aISLM
BROADCAST_MODE=sync

$HAQQD_BIN tx gov vote $PROPOSAL_ID $VOTE --from $VAL_NAME --yes --node $RPC_URL --gas-adjustment=$GAS_ADJUSTMENT --broadcast-mode $BROADCAST_MODE --gas=auto --gas-prices $GAS_PRICES --chain-id=$CHAIN_ID
