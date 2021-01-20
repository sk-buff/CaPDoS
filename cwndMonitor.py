#!/bin/python3
import getopt
import socket
import sys
import time
import re
import ipaddress

interval = 10
monitorRules = []
sampleTimes = None
results = {}

pseudoIPPattern = "[0-9]+.[0-9]+.[0-9]+.[0-9]+"
flowInfoPattern = "(%s)(:[0-9]+)?((-%s)(:[0-9]+)?)?" % (pseudoIPPattern, pseudoIPPattern)
flowInfoParseErrorInfo = """plz input --flowinfo in the format of IP1[:port1][-IP2[:port2]], e.g. 
--flowinfo=10.0.0.1:1024-10.0.0.2:22, your input is %s"""

def parseArgs(argList):
    global interval, monitorRules, sampleTimes
    paramList = ["interval=", "flowinfo=", "times="]

    params, restArgs = getopt.getopt(argList, "", paramList)

    for k, v in params:
        if k == "--interval":
            try:
                interval = int(v)
            except:
                print("plz input an interger after --interval=, e.g. --interval=10")
                return -1

        elif k == "--flowinfo":
            res = re.search(flowInfoPattern, v)
            if res == None:
                print(flowInfoParseErrorInfo % v)
                return -1
           
            IP1, port1, IP2, port2 = res[1], res[2], res[4], res[5]

            # parse IP1
            try:
                IP1 = ipaddress.IPv4Address(IP1)
            except:
                print("IP1 is not a valid IP address")
                return -1

            IP1 = ("%08x" % socket.htonl(int(IP1))).upper()
    
            # parse port1
            if port1 == None:
                port1 = ""
            else:
                try:
                    port1 = port1[1:]
                    port1 = int(port1)
                except:
                    print("port1 is not an integer")
                    return -1

                if not(0 <= port <= 65535):
                    print("plz make sure port1 is in the range of 0-65535")
                    return -1

                port1 = ("%04x" % port1).upper()

            # parse IP2
            if IP2 == None:
                IP2 = ""
            else:
                try:
                    IP2 = IP2[1:]
                    IP2 = ipaddress.IPv4Address(IP2)
                except:
                    print("IP2 is not a valid IP address")
                    return -1

                IP2 = ("%08x" % socket.htonl(int(IP2))).upper()

            # parse port2
            if port2 == None:
                port2 = ""
            else:
                try:
                    port2 = port2[1:]
                    port2 = int(port2)
                except:
                    print("port2 is not an integer")
                    return -1

                if not(0 <= port <= 65535):
                    print("plz make sure port2 is in the range of 0-65535")
                    return -1

                port2 = ("%04x" % port2).upper()

            monitorRules.append((IP1, port1, IP2, port2))
        
        elif k == "--times":
            try:
                sampleTimes = int(v)
            except:
                print("plz input an interger after --times=, e.g. --times=10")
                return -1

    if sampleTimes == None:
        print("plz input --times parameter")
        return -1

    if monitorRules == []:
        print("plz input at least one --flowinfo parameter")
        return -1

    return 0      

if __name__ == "__main__":
    ret = parseArgs(sys.argv[1:])
    if ret == -1:
        sys.exit(0)

    TCPFlowInfo = []
    f = open("/proc/net/tcp")
    for i in range(sampleTimes):
        TCPFlowInfo.append(f.read())
        f.seek(0)
        time.sleep(interval / 1000)
    
    for i in range(len(TCPFlowInfo)):
        oneTCPFlowInfoItem = TCPFlowInfo[i]
        lines = oneTCPFlowInfoItem.split("\n")
        for line in lines:
            for oneRule in monitorRules:
                if (oneRule[0] in line and oneRule[1] in line and 
                    oneRule[2] in line and oneRule[3] in line):
                    splitLine = line.split()
                    flowIP1, flowPort1 = splitLine[1].split(':')
                    flowIP1 = str(ipaddress.IPv4Address(socket.ntohl(int(flowIP1, 16))))
                    flowPort1 = int(flowPort1, 16)
                    flowIP2, flowPort2 = splitLine[2].split(':')
                    flowIP2 = str(ipaddress.IPv4Address(socket.ntohl(int(flowIP2, 16))))
                    flowPort2 = int(flowPort2, 16)
                    cwndSize = splitLine[-2]

                    index = "%s:%s-%s:%s" % (flowIP1, flowPort1, flowIP2, flowPort2) 
                    if index not in results:
                        results[index] = {}

                    results[index][i] = cwndSize

    for oneFlow in results:
        print(oneFlow)
        for t in results[oneFlow]:
            print("%4s" % t, end='')
        print('')
        for t in results[oneFlow]:
            print("%4s" % results[oneFlow][t], end='')
        print('\n')

                    
