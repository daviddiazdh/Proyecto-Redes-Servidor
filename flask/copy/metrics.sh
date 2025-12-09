#!/bin/bash
OUTPUT="metrics.csv"

if [ ! -f "$OUTPUT" ]; then
    echo "timestamp,cpu,mem,disk,net_sent,net_recv" > "$OUTPUT"
fi

while true; do
    DATA=$(curl -s http://localhost:5000/metrics)
    CPU=$(echo $DATA | jq .cpu)
    MEM=$(echo $DATA | jq .mem)
    DISK=$(echo $DATA | jq .disk)
    SENT=$(echo $DATA | jq .net_sent)
    RECV=$(echo $DATA | jq .net_recv)
    echo "$(date +%s),$CPU,$MEM,$DISK,$SENT,$RECV" >> "$OUTPUT"
    sleep 5
done