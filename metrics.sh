#!/bin/bash
OUTPUT="metrics.csv"
INTERVAL=1   # segundos entre mediciones

if [ ! -f "$OUTPUT" ]; then
    echo "timestamp;cpu;mem" > "$OUTPUT"
fi

# -------- CPU: valores iniciales --------
read _ user_prev nice_prev system_prev idle_prev iowait_prev irq_prev softirq_prev steal_prev guest_prev guest_nice_prev < /proc/stat

while true; do
    TIMESTAMP=$(date +%s)

    # -------- CPU USAGE REAL --------
    read _ user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat

    idle_delta=$((idle - idle_prev))

    prev_total=$((user_prev + nice_prev + system_prev + idle_prev + iowait_prev + irq_prev + softirq_prev))
    total=$((user + nice + system + idle + iowait + irq + softirq))

    total_delta=$((total - prev_total))

    # --- Protección contra división por cero ---
    if [ "$total_delta" -eq 0 ]; then
        CPU=0
    else
        CPU=$(( 100 * (total_delta - idle_delta) / total_delta ))
    fi

    # Guardar valores para la siguiente iteración
    user_prev=$user
    nice_prev=$nice
    system_prev=$system
    idle_prev=$idle
    iowait_prev=$iowait
    irq_prev=$irq
    softirq_prev=$softirq

    # -------- MEMORIA --------
    MEM=$(free | awk '/Mem:/ {printf("%.1f", $3/$2 * 100)}')

    echo "$TIMESTAMP;$CPU;$MEM" >> "$OUTPUT"

    sleep $INTERVAL
done