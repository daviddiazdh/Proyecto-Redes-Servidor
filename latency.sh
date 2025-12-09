#!/bin/bash

if [ ! -f "latency.csv" ]; then
    echo "timestamp;response_time" > latency.csv
fi


while true; do
    ts=$(date +%s)
    t=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:5000/)
    echo "$ts;$t" >> latency.csv
    sleep 1
done