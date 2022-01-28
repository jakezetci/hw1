#!/usr/bin/env python3

from scipy.io import netcdf
import numpy as np
import json
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('longitude', metavar='LON', type=float, help='Longitude, deg')
parser.add_argument('latitude',  metavar='LAT', type=float, help='Latitude, deg')

if __name__ == "__main__":
    args = parser.parse_args()
    print(args.longitude, args.latitude)
    f = netcdf.netcdf_file('MSR-2.nc', 'r', mmap=False)
    variables = f.variables
    n_of_months = variables['time'].shape[0]
    lat_index = np.searchsorted(variables['latitude'].data, args.latitude)
    lon_index = np.searchsorted(variables['longitude'].data, args.longitude)
    d = {}
    d["coordinates"] = [args.longitude,args.latitude]
    months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    maxi = np.zeros(3)
    mini = np.asarray([1e10,1e10,1e10])
    mean = np.zeros(3)
    names = ['jan','jul','all']
    dots = [[],[],[]]
    for i in range (int(n_of_months)):   
        data = variables['Average_O3_column'][i,lat_index,lon_index].copy()
        dot = (data, 1979+i/12)
        mean[2] += data
        dots[2].append(dot)
        if data > maxi[2]:
            maxi[2] = data
        if data < mini[2]:
            mini[2] = data
        if (i % 12 == 0):
            mean[1] += data
            dots[1].append(dot)
            if data > maxi[1]:
                maxi[1] = data
            if data < mini[1]:
                mini[1] = data
                
        elif (i % 12 == 5):
            mean[0] += data
            dots[0].append(dot)
            if data > maxi[0]:
                maxi[0] = data
            if data < mini[0]:
                mini[0] = data
    mean[2] = int(mean[2])/504
    mean[1] = int(mean[1])/42
    mean[0] = int(mean[0])/42
    for k in range(3):
        d[names[k]] = {
            "min":int(mini[k]),
            "max":int(maxi[k]),
            "mean":mean[k]}
    
    with open('ozon.json', 'w') as f:   
            json.dump(d, f)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel('years')
    ax.set_ylabel('ozon column')
    january = np.transpose(dots[0])
    july = np.transpose(dots[1])
    overall = np.transpose(dots[2])
    plt.plot(january[1],january[0], 'b')
    plt.plot(july[1], july[0], 'g')
    plt.plot(overall[1], overall[0], 'r')
    
    plt.savefig('ozon.png')