#!/usr/bin/env python3

import sys, getopt

def parse_args(argv):
    try:
        options, args = getopt.getopt(argv,"a:r:",["analyze=", "report="])
    except getopt.GetoptError:
        print("Usage: 'client.py --analyze=address' or 'client.py --report=address'")
        sys.exit(2)

    for option, arg in options:
        if option in ("-a", "--analyze"):
            print("Analizar " + arg)
        elif option in ("-r", "--report"):
            print("Reporte de " + arg)

if __name__ == "__main__":
    parse_args(sys.argv[1:])
