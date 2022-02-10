#!/usr/bin/env python3

from scipy.io import netcdf
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
import argparse
from geopy.geocoders import Nominatim


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


parser = argparse.ArgumentParser()
parser.add_argument('pos', metavar='POS', type=str,
                    help='Position: location name or "longitude  latitude"',
                    default=None, nargs='*')
args = parser.parse_args()

if is_float(args.pos[0]) and is_float(args.pos[1]):
    if len(args.pos) != 2:
        raise NotImplementedError("wrong format")
    longitude = float(args.pos[0])
    latitude = float(args.pos[1])


if __name__ == "__main__":
    f = netcdf.netcdf_file('MSR-2.nc', 'r', mmap=False)
    variables = f.variables
    n_of_months = variables['time'].shape[0]
    # ближайшие подходящие координаты
    lat_index = np.searchsorted(variables['latitude'].data, latitude)
    lon_index = np.searchsorted(variables['longitude'].data, longitude)
    d = {}
    d["coordinates"] = [longitude, latitude]
    maxi = np.zeros(3)  # массивы для хранения данных под словарь
    mini = np.asarray([1e10, 1e10, 1e10])
    mean = np.zeros(3)
    names = ['jan', 'jul', 'all']  # интересующая нас дата
    dots = [[], [], []]  # массив для создания точек под графики
    for i in range(int(n_of_months)):
        data = variables['Average_O3_column'][i, lat_index, lon_index].copy()
        dot = (data, 1979+i/12)
        mean[2] += data
        dots[2].append(dot)
        if data > maxi[2]:
            maxi[2] = data
        if data < mini[2]:
            mini[2] = data
        if (i % 12 == 0):
            mean[0] += data
            dots[0].append(dot)
            if data > maxi[0]:
                maxi[0] = data
            if data < mini[0]:
                mini[0] = data
        elif (i % 12 == 5):
            mean[1] += data
            dots[1].append(dot)
            if data > maxi[1]:
                maxi[1] = data
            if data < mini[1]:
                mini[1] = data
    mean[2] = np.round(float(mean[2])/n_of_months, decimals=2)
    mean[1] = np.round(float(mean[1])*12/n_of_months, decimals=2)
    mean[0] = np.round(float(mean[0])*12/n_of_months, decimals=2)
    for k in range(len(names)):
        d[names[k]] = {
            'min': float(mini[k]),
            'max': float(maxi[k]),
            'mean': mean[k]}
    with open('ozon.json', 'w') as f:
        json.dump(d, f)

    """построение графиков"""
    fig = plt.figure(figsize=(20, 9))
    ax = fig.add_subplot(1, 1, 1)
    ax.spines['bottom'].set_position(['axes', 0.0])
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel('years', fontfamily="Calibri", fontsize='xx-large')
    ax.set_ylabel('ozon column, Dobson units', fontfamily='Calibri',
                  fontsize='xx-large')
    january = np.transpose(dots[0])
    july = np.transpose(dots[1])
    overall = np.transpose(dots[2])
    jan_plot, = plt.plot(january[1], january[0], 'b', ls='--')
    jul_plot, = plt.plot(july[1], july[0], 'red', ls='--')
    all_plot, = plt.plot(overall[1], overall[0], 'grey', lw=1)
    plt.fill_between(overall[1], overall[0], color='grey', alpha=0.4)
    jan_plot.set_label('ozone level during january')
    jul_plot.set_label('ozone level during july')
    all_plot.set_label('ozone level throughout the years')
    ax.set_ylim([mini[2]-5.0, maxi[2]+5.0])
    ax.legend(loc='best')
    plt.savefig('ozon.png')
