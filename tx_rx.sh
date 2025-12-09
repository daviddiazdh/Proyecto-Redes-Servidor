#!/bin/bash

if [ ! -f "tx_rx.csv" ]; then
    echo "timestamp;bytes_rx;bytes_tx" > tx_rx.csv
fi

IFACE=wlx0011958d86c9

prev_rx=$(cat /sys/class/net/$IFACE/statistics/rx_bytes)
prev_tx=$(cat /sys/class/net/$IFACE/statistics/tx_bytes)

while true; do
    sleep 1

    ts=$(date +%s)

    curr_rx=$(cat /sys/class/net/$IFACE/statistics/rx_bytes)
    curr_tx=$(cat /sys/class/net/$IFACE/statistics/tx_bytes)

    rx_rate=$((curr_rx - prev_rx))
    tx_rate=$((curr_tx - prev_tx))

    echo "$ts;$rx_rate;$tx_rate" >> tx_rx.csv

    prev_rx=$curr_rx
    prev_tx=$curr_tx
    
done