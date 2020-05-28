#!/bin/bash

# Output CSV-formatted statistics about each process using > ${threshold}% CPU,
# sampling every ${delay} seconds. Assume we'll find them in the top ${max}
# processes returned by `top` sorting by CPU usage.

# arguments
threshold=$1
delay=$2
max=$3

echo "Threshold: ${threshold}% CPU. Sampling every ${delay} seconds." > /dev/stderr

echo "Timestamp,Process,CPU"
while True
do
    ps aux -c -r | tail -n +2 | head -n ${max} | while read -r line
    do
        cpu=$(echo "${line}" | awk '{print $3}')
        process=$(echo "${line}" | awk '{print $11}')
        # need more names of process??
        timestamp=$(date +"%Y-%m-%d %H:%M:%S")

        if (( $(echo "${cpu} >= ${threshold}" | bc -l) ))
        then
            echo "${timestamp},${process},${cpu}"
        fi
    done
    echo "." > /dev/stderr
    sleep ${delay}
done
