#!/usr/bin/python3

import pickle
import sys
import getopt
import ipaddress
import random
from scapy.all import *
from scapy.utils import PcapWriter

pktPickleData = b'\x80\x04\x95\x99\x00\x00\x00\x00\x00\x00\x00\x8c\x0fscapy.layers.l2\x94\x8c\x05Ether\x94\x93\x94)R\x94(C:\x14\x18wV3\x80\x14\x18wQC\t\x08\x00E\x00\x00,\xde\xd7@\x00@\x06F\xeb\n\x00\x00\x84\n\x00\x00\x86\xeb\xf8\x1f@!=w\x9a\x00\x00\x00\x00`\x02r\x10\x15(\x00\x00\x02\x04\x05\xb4\x94\x8c\x0bscapy.utils\x94\x8c\x08EDecimal\x94\x93\x94\x8c\x111609232535.231704\x94\x85\x94R\x94NNNK:t\x94b.'

def parseArgs(argList):
    pktNum = None
    pktLen = None
    dstIPAddress = None
    dstPort = None
    outPutFileName = None

    shortargs, argList = getopt.getopt(argList, "n:l:a:p:o:")
    for k, v in shortargs:
        if k == "-n":
            try:
                pktNum = int(v)
            except:
                print("Plz input a integer after -n, e.g. -n 100")
                return -1
        elif k == "-l":
            try:
                pktLen = int(v)
            except:
                print("Plz input a integer after -l, e.g. -l 100")
                return -1
        elif k == "-a":
            try:
                ipaddress.IPv4Address(v)
                dstIPAddress = v
            except:
                print("Plz input a valid ipv4 address after -a, e.g. -a 10.0.0.1")
                return -1
        elif k == "-p":
            try:
                dstPort = int(v)
            except:
                print("Plz input a integer after -p, e.g. -p 12345")
                return -1
            
            if not(0 <= dstPort <= 65535):
                print("port number should in the range of 0-65535")
                return -1
        elif k == "-o":
            outPutFileName = v
        
    if None in (pktNum, pktLen, dstIPAddress, dstPort, outPutFileName):
        print("Not enough parameters are entered, make sure -n, -l, -a, -p, -o are entered")
        return -1

    return (pktNum, pktLen, dstIPAddress, dstPort, outPutFileName)

def generateTrace(pktNum, pktLen, dstIPAddress, dstPort, outPutFileName):
    seedPkt = pickle.loads(pktPickleData)
    pktList = []

    writer = PcapWriter(outPutFileName)

    seedPkt[IP].dst = dstIPAddress
    seedPkt[TCP].dport = dstPort
    for i in range(pktNum):
        while True:
            srcIPAddress = ipaddress.IPv4Address(random.randint(0, 4294967295))
            if srcIPAddress.is_global == True:
                srcIPAddress = str(srcIPAddress)
                break

        pkt = seedPkt/Raw()
        pkt[IP].src = srcIPAddress
        pkt[TCP].sport = random.randint(10000, 65535)
        pkt[Raw].load = (pktLen - len(pkt)) * "\x00"
        pkt[IP].len = pktLen - 14
        pkt.wirelen = pktLen
        # del pkt[IP].chksum
        # del pkt[TCP].chksum

        writer.write(pkt)

def main():
    ret = parseArgs(sys.argv[1:])
    if ret == -1:
        return -1

    generateTrace(*ret)

# sys.argv = "./traceGen.py -n 100 -l 100 -a 10.0.0.1 -p 80 -o res".split(" ")
main()
