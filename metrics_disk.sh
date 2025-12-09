#!/bin/bash
OUTPUT="metrics_disk.csv"
INTERVAL=1

# Detectar disco principal
DISK_DEV=$(lsblk -ndo NAME,TYPE | awk '$2=="disk"{print $1; exit}')

if [ ! -f "$OUTPUT" ]; then
    echo "timestamp;disk;read_bps;write_bps" > "$OUTPUT"
fi

# Función para obtener I/O inicial
get_disk_io() {
    awk -v dev="$DISK_DEV" '$3==dev {print $6, $10}' /proc/diskstats
}

# Lecturas previas
read PREV_READ PREV_WRITE <<< "$(get_disk_io)"

while true; do
    TIMESTAMP=$(date +%s)

    # Uso de disco raíz
    DISK=$(df / | awk 'NR==2 {print $5}' | tr -d '%')

    # I/O actual
    read READ WRITE <<< "$(get_disk_io)"

    # Bytes por segundo
    READ_BPS=$((READ - PREV_READ))
    WRITE_BPS=$((WRITE - PREV_WRITE))

    PREV_READ=$READ
    PREV_WRITE=$WRITE

    echo "$TIMESTAMP;$DISK;$READ_BPS;$WRITE_BPS" >> "$OUTPUT"

    sleep $INTERVAL
done