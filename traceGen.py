#!/usr/bin/python3

import pickle
import sys
import getopt
import ipaddress
import random
from scapy.all import *
from scapy.utils import PcapWriter
import re

pktPickleData = b'\x80\x04\x95\x99\x00\x00\x00\x00\x00\x00\x00\x8c\x0fscapy.layers.l2\x94\x8c\x05Ether\x94\x93\x94)R\x94(C:\x14\x18wV3\x80\x14\x18wQC\t\x08\x00E\x00\x00,\xde\xd7@\x00@\x06F\xeb\n\x00\x00\x84\n\x00\x00\x86\xeb\xf8\x1f@!=w\x9a\x00\x00\x00\x00`\x02r\x10\x15(\x00\x00\x02\x04\x05\xb4\x94\x8c\x0bscapy.utils\x94\x8c\x08EDecimal\x94\x93\x94\x8c\x111609232535.231704\x94\x85\x94R\x94NNNK:t\x94b.'

def parseArgs(argList):
    pulsePktParams = ["pktNum=", "pktLen=", "srcMac=", "dstMac=", 
                      "srcIP=", "dstIP=", "srcPort=", "dstPort="]
    nonePulsePktParams = ["nonPulsePktNum=", "nonPulsePktLen=", "nonPulsePktDstMac=", 
                          "nonPulsePktDstIP=", "nonPulsePktDstPort="]
    otherParams = ["outputFile="]
    pktNum = None
    pktLen = None
    srcMac = None
    dstMac = None
    srcIP = None
    dstIP = None
    srcPort = None
    dstPort = None
    outputFile = None
    nonPulsePktNum = None
    nonPulsePktLen = None
    nonPulsePktDstMac = None
    nonPulsePktDstIP = None
    nonPulsePktDstPort = None

    args, argList = getopt.getopt(argList, "", pulsePktParams+nonePulsePktParams+otherParams)
    for k, v in args:
        if k == "--pktNum":
            try:
                pktNum = int(v)
            except:
                print("Plz input a integer after --pktNum, e.g. --pktNum=100")
                return -1
        elif k == "--pktLen":
            try:
                pktLen = int(v)
            except:
                print("Plz input a integer after --pktLen, e.g. --pktLen=100")
                return -1
        elif k == "--srcMac":
            if re.match("([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", v) == None:
                print("Plz input a valid mac address after --srcMac, e.g. --srcMac=08:00:27:87:b5:5d")
                return -1
            else:
                srcMac = v
        elif k == "--dstMac":
            if re.match("([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", v) == None:
                print("Plz input a valid mac address after --dstMac, e.g. --dstMac=08:00:27:87:b5:5d")
                return -1
            else:
                dstMac = v
        elif k == "--srcIP":
            try:
                ipaddress.IPv4Address(v)
                srcIP = v
            except:
                print("Plz input a valid ipv4 address after --srcIP, e.g. --srcIP=10.0.0.1")
                return -1
        elif k == "--dstIP":
            try:
                ipaddress.IPv4Address(v)
                dstIP = v
            except:
                print("Plz input a valid ipv4 address after --dstIP, e.g. --dstIP=10.0.0.1")
                return -1
        elif k == "--srcPort":
            try:
                srcPort = int(v)
            except:
                print("Plz input a integer after --srcPort, e.g. --srcPort=12345")
                return -1
            
            if not(0 <= srcPort <= 65535):
                print("srcPort number should be in the range of 0-65535")
                return -1
        elif k == "--dstPort":
            try:
                dstPort = int(v)
            except:
                print("Plz input a integer after --dstPort, e.g. --dstPort=12345")
                return -1
            
            if not(0 <= dstPort <= 65535):
                print("dstPort number should be in the range of 0-65535")
                return -1
        elif k == "--nonPulsePktNum":
            try:
                nonPulsePktNum = int(v)
            except:
                print("Plz input a integer after --nonPulsePktNum, e.g. --nonPulsePktNum=100")
                return -1
        elif k == "--nonPulsePktLen":
            try:
                nonPulsePktLen = int(v)
            except:
                print("Plz input a integer after --nonPulsePktLen, e.g. --nonPulsePktLen=1000")
                return -1
        elif k == "--nonPulsePktDstMac":
            if re.match("([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", v) == None:
                print("Plz input a valid mac address --nonPulsePktDstMac, e.g. --nonPulsePktDstMac=08:00:27:87:b5:5d")
                return -1
            else:
                nonPulsePktDstMac = v
        elif k == "--nonPulsePktDstIP":
            try:
                ipaddress.IPv4Address(v)
                nonPulsePktDstIP = v
            except:
                print("Plz input a valid ipv4 address after --nonPulsePktDstIP, e.g. --nonPulsePktDstIP=10.0.0.1")
                return -1
        elif k == "--nonPulsePktDstPort":
            try:
                nonPulsePktDstPort = int(v)
            except:
                print("Plz input a integer after --nonPulsePktDstPort, e.g. --nonPulsePktDstPort=12345")
                return -1
            
            if not(0 <= dstPort <= 65535):
                print("--nonPulsePktDstPort port number should in the range of 0-65535")
                return -1
        elif k == "--outputFile":
            outputFile = v

    if None in (pktNum, pktLen, srcMac, dstMac, srcIP, dstIP, srcPort, dstPort, outputFile):
        print("""Not enough parameters are entered, make sure --pktNum, --pktLen, --srcMac, 
        --dstMac, --srcIP, --dstIP, --srcPort, --dstPort, --outPutFileName, are entered""")
        return -1

    if nonPulsePktNum != None and None in [nonPulsePktDstMac, nonPulsePktDstIP, nonPulsePktDstPort]:
        print("""after --nonPulsePktDstMac, --nonPulsePktDstMac, --nonPulsePktDstIP
              and --nonPulsePktDstPort are needed""")
        return -1

    return (pktNum, pktLen, srcMac, dstMac, srcIP, dstIP, srcPort, dstPort, outputFile,
            nonPulsePktNum, nonPulsePktLen, nonPulsePktDstMac, nonPulsePktDstIP, nonPulsePktDstPort)

def generateTrace(pktNum, pktLen, srcMac, dstMac, srcIP, dstIP, srcPort, dstPort, outPutFileName,
                  nonPulsePktNum=None, nonPulsePktLen=None, nonPulsePktDstMac=None,
                  nonPulsePktDstIP=None, nonPulsePktDstPort=None):
    seedPkt = pickle.loads(pktPickleData)
    seedPktLen = len(seedPkt)

    writer = PcapWriter(outPutFileName)

    pkt = seedPkt/Raw()
    pkt[Ether].src = srcMac
    pkt[Ether].dst = dstMac
    pkt[IP].src = srcIP
    pkt[IP].dst = dstIP
    pkt[TCP].sport = srcPort
    pkt[TCP].dport = dstPort
    pkt[Raw].load = (pktLen - seedPktLen) * "\x00"
    pkt[IP].len = pktLen - 14
    pkt.wirelen = pktLen
    """for i in range(pktNum):
        if randSrcIP == True:
            while True:
                srcIPAddress = ipaddress.IPv4Address(random.randint(0, 4294967295))
                if srcIPAddress.is_global == True:
                    srcIPAddress = str(srcIPAddress)
                    break
            
            pkt[IP].src = srcIPAddress"""

    for i in range(pktNum):
        writer.write(pkt)

    if type(nonPulsePktNum) is int:
        if nonPulsePktLen == None:
            nonPulsePktLen = pktLen

        pkt[Ether].dst = nonPulsePktDstMac
        pkt[IP].dst = nonPulsePktDstIP
        pkt[TCP].dport = nonPulsePktDstPort
        pkt[Raw].load = (nonPulsePktLen - seedPktLen) * "\x00"
        pkt[IP].len = nonPulsePktLen - 14

        for i in range(nonPulsePktNum):
            writer.write(pkt)

def main():
    ret = parseArgs(sys.argv[1:])
    if ret == -1:
        return -1

    generateTrace(*ret)

# sys.argv = "./traceGen.py --pktNum=100 --pktLen=1000 --srcMac=14:18:77:51:43:06 --dstMac=14:18:77:54:2e:4c --srcIP=101.6.30.132 --dstIP=101.6.30.136 --srcPort=12345 --dstPort=80 --nonPulsePktNum=900 --nonPulsePktLen=1000 --nonPulsePktDstMac=14:18:77:53:4e:ef --nonPulsePktDstIP=101.6.30.137 --nonPulsePktDstPort=80 --outputFile=asd.pcap".split(" ")
main()
