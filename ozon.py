#!/usr/bin/env python3

from scipy.io import netcdf
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib
import argparse

import os

try:
    from geopy.geocoders import Nominatim

except ImportError:
    os.system('pip3 install geopy')
    from geopy.geocoders import Nominatim


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


def location_font(location):
    """
    finds the appropriate font for your location
    :param location: your location
    :type location: location.Location
    :return: fontstyle
    :rtype: matplotlib.font_manager.FontProperties

    """
    style = matplotlib.font_manager.FontProperties()
    style.set_size('xx-large')
    style.set_family(['Calibri', 'Helvetica', 'Arial', 'serif'])
    addr_dict = location.raw["address"]
    keys = ['jp', 'cn', 'kr', 'kp', 'mm', 'mn', 'th']
    countries_dict = {
        'cn': "SimSun",
        'th': "Leelawadee UI",
        'kr': 'Malgun Gothic',
        'jp': 'MS Gothic',
        'kp': 'Malgun Gothic',
        'mm': "Myanmar Text",
        'mn': "Mongolian Baiti"
                     }  # не панацея, но кажется, это все языки вне Calibri
    if 'country_code' in addr_dict:
        code = addr_dict['country_code']
    else:
        return style
    if code in keys:
        style.set_family([countries_dict[code],
                         'Calibri', 'Helvetica', 'Arial', 'serif'])
    return style
#  вообще проблему языков и шрифтов должен решать familyfont, а не моя функция
#  но матплотлиб его использует лишь для проверки существования шрифта в целом,
#  а не каждого глифа

#  а, и ещё надо бы создать для каждого языка целую семью шрифтов, но мне лень
#  если у вас не нашлось этого шрифта на компе - простите уж, могу поправить


def location_city(location):
    """
    shortens the location.address to just city/village + country or smth else
    :param location: your location with location.raw["address"] available
    :type location: location.Location
    :return: short format of an address or None if there is no address
    :rtype: str

    """
    village_KEYS = ['city', 'town', 'village', 'hamlet', 'municipality']
    addr_dict = location.raw["address"]
    for key in village_KEYS:
        if key in addr_dict:
            return ("".join([addr_dict["country"], ", ", addr_dict[key]]))
    if 'locality' in addr_dict and 'country' in addr_dict:
        return("".join([addr_dict["country"], ", ", addr_dict['locality']]))
    elif 'country' in addr_dict:
        return(addr_dict['country'])
    elif 'locality' in addr_dict:
        return(addr_dict['locality'])
    else:
        latitude = addr_dict['lat']
        longitude = addr_dict['lon']
        return(f'{latitude}, {longitude}')


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
    geolocator = Nominatim(user_agent="Ozone Stuff")
    lat_long = " ".join(str(e) for e in args.pos[::-1])
    # приходится реверсить потому что в задании просят сначала подавать долготу
    location = geolocator.reverse(lat_long)
else:
    if len(args.pos) == 1:
        loc = args.pos
    else:
        loc = " ".join(str(e) for e in args.pos)
    geolocator = Nominatim(user_agent="Ozone Stuff")
    location = geolocator.geocode(loc)
    if location is None:
        raise NotImplementedError("wrong format")
    latitude = location.latitude
    longitude = location.longitude
    a = " ".join(str(e) for e in [latitude, longitude])
    # такой некрасивый переворот происходит из-за неоднозначности geopy,
    # иначе он не даст нужного location.raw
    location = geolocator.reverse(a)


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
    for i in range(int(n_of_months)):  # цикл O(n), быстрее, наверное, нельзя
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
        elif (i % 12 == 6):
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
    style_default = matplotlib.font_manager.FontProperties()
    style_default.set_size('xx-large')
    style_default.set_family(['Calibri', 'Helvetica', 'Arial', 'serif'])
    january = np.transpose(dots[0])
    july = np.transpose(dots[1])
    overall = np.transpose(dots[2])
    ax = fig.add_subplot(1, 1, 1)
    ax.spines['bottom'].set_position(['axes', 0.0])
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.xticks(np.arange(min(overall[1])-1, max(overall[1])+1, 6.0),
               fontsize='large')
    # немного замедляет, но зато сработает с любым датасетом
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel('years', fontproperties=style_default)
    ax.set_ylabel('ozon column, Dobson units', fontproperties=style_default)
    jan_plot, = plt.plot(january[1], january[0], 'b', ls='--')
    jul_plot, = plt.plot(july[1], july[0], 'red', ls='--')
    all_plot, = plt.plot(overall[1], overall[0], 'grey', lw=1)
    plt.fill_between(overall[1], overall[0], color='grey', alpha=0.4)
    jan_plot.set_label('ozone level during january')
    jul_plot.set_label('ozone level during july')
    all_plot.set_label('ozone level throughout the years')
    if location is not None:  # предотвращает случаи поиска селения в океане
        style = location_font(location)
        plt.title(location_city(location), fontproperties=style)
    else:
        plt.title(f'{latitude}, {longitude}', fontproperties=style_default)
    ax.set_ylim([mini[2]-5.0, maxi[2]+5.0])
    ax.legend(loc='best', prop=style_default)
    plt.grid()
    plt.savefig('ozon.png')
