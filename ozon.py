#!/usr/bin/env python3

from scipy.io import netcdf
import numpy as np
import json
import matplotlib.pyplot as plt
import argparse
from geopy.geocoders import Nominatim


def location_city(location):
    village_KEYS = ['city', 'town', 'village', 'hamlet']
    
    addr_dict = location.raw["address"]
    for key in village_KEYS:
        if key in addr_dict:
            return ("".join([addr_dict["country"],", ",addr_dict[key]]))


parser = argparse.ArgumentParser()
parser.add_argument('pos', metavar='POS', type=str, help='Position, location name or "longitude  latitude"', default = None, nargs = '*')
args = parser.parse_args()
if len(args.pos) == 1:
    loc = args.pos
    geolocator = Nominatim(user_agent="Ozone Stuff")
    location = geolocator.geocode(loc)
    latitude = location.latitude
    longitude = location.longitude
    a = " ".join(str(e) for e in [latitude, longitude])
#такой некрасивый переворот происходит из-за неоднозначности geopy, иначе он не даст нужного location.raw
    location = geolocator.reverse(a)
elif len(args.pos) == 2:
    longitude = float(args.pos[0])
    latitude = float(args.pos[1])
    geolocator = Nominatim(user_agent="Ozone Stuff")
    a = " ".join(str(e) for e in args.pos[::-1]) #приходится реверсить потому что в задании зачем-то просят сначала подавать долготу
    location = geolocator.reverse(a)
else:
    print("wrong format")


if __name__ == "__main__":
    f = netcdf.netcdf_file('MSR-2.nc', 'r', mmap=False)
    variables = f.variables
    n_of_months = variables['time'].shape[0]
    lat_index = np.searchsorted(variables['latitude'].data, latitude)
    lon_index = np.searchsorted(variables['longitude'].data, longitude)
    d = {}
    d["coordinates"] = [longitude,latitude]
    maxi = np.zeros(3)# массивы для хранения данных под словарь
    mini = np.asarray([1e10,1e10,1e10])
    mean = np.zeros(3)
    names = ['jan','jul','all']#интересующая нас дата 
    dots = [[],[],[]] #массив для создания точек
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
    mean[2] = int(mean[2])/504
    mean[1] = int(mean[1])/42
    mean[0] = int(mean[0])/42
    for k in range(3):
        d[names[k]] = {
            'min':int(mini[k]),
            'max':int(maxi[k]),
            'mean':mean[k]}
    
    with open('ozon.json', 'w') as f:   
            json.dump(d, f)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.spines['bottom'].set_position(['axes', 0.0])
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel('years')
    ax.set_ylabel('ozon column')
    january = np.transpose(dots[0])
    july = np.transpose(dots[1])
    overall = np.transpose(dots[2])
    a, = plt.plot(january[1],january[0],'b', ls='--')
    b, = plt.plot(july[1], july[0], 'g', ls='--')
    c, = plt.plot(overall[1], overall[0], 'r', lw=0.4)
    a.set_label('january')
    b.set_label('july')
    c.set_label('all data')
    if location is not None:
        d, = plt.plot([],[], 'o')
        c = location.address
        b = location
        d.set_label(location_city(location))
    ax.legend()
    plt.savefig('ozon.png')
    