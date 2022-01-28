#!/usr/bin/env python3

import json
import sys
from numpy.testing import assert_almost_equal

with open(sys.argv[1]) as json_file:
    data = json.load(json_file)

    assert_almost_equal(data['coordinates'][0], 18.96, 2)
    assert_almost_equal(data['coordinates'][1], 69.66, 2)
    assert_almost_equal(data['jan']['min'], 233.0, 0)
    assert_almost_equal(data['jan']['max'], 258.0, 0)
    assert_almost_equal(data['jan']['mean'], 246.8, 0)
    assert_almost_equal(data['jul']['min'], 265.0, 0)
    assert_almost_equal(data['jul']['max'], 286.0, 0)
    assert_almost_equal(data['jul']['mean'], 277.7, 0)
    assert_almost_equal(data['all']['min'], 232.0, 0)
    assert_almost_equal(data['all']['max'], 295.0, 0)
    assert_almost_equal(data['all']['mean'], 266.1, 0)
