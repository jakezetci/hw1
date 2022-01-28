#!/usr/bin/env python3

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('longitude', metavar='LON', type=float, help='Longitude, deg')
parser.add_argument('latitude',  metavar='LAT', type=float, help='Latitude, deg')

if __name__ == "__main__":
    args = parser.parse_args()
    print(args.longitude, args.latitude)
