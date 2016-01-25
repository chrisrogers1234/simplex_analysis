import os
import subprocess
import json
import operator
import sys

import numpy
import ROOT

import Configuration
import maus_cpp.globals

from scipy.spatial import Delaunay


import xboa.common as common
from xboa.bunch import Bunch
from xboa.hit import Hit
from xboa.tracking import MAUSTracking
from xboa.bunch.weighting import VoronoiWeighting
from xboa.bunch.weighting import BoundingEllipse
import xboa.bunch.weighting._hull_content

import analysis

def get_hit(x, y, z, t, px, py, pz):
    hit_dict = {
        'mass':common.pdg_pid_to_mass[13],
        'pid':-13,
        'x':x,
        'y':y,
        'z':z,
        'px':px,
        'py':py,
        'pz':pz,
        't':0.
    }
    hit = Hit.new_from_dict(hit_dict, 'energy')
    return hit

def do_one(tracking, seed_hit, delta):
    variables = delta.keys()
    print "    ... tracking", [(var, seed_hit[var]) for var in ['x', 'px', 'y', 'py', 't', 'energy', 'z', 'pz']]
    bunch_list = tracking.track(
        seed_hit,
        delta
    )
    print "    ... analysis"
    bunch_list = [bunch for bunch in bunch_list if bunch[0]['z'] < 3610.]
    areas = tracking.delaunay(variables)
    areas = [areas[i] for i in range(len(bunch_list))]
    an_area_list, area_list_of_lists = [], []
    for i, bunch_area in enumerate(areas): 
        bunch = bunch_list[i]
        test_coords = [[hit[var] for var in variables] for hit in bunch[0:len(variables)+1]]
        an_area = xboa.bunch.weighting._hull_content._tile_content(
                (range(len(test_coords)), test_coords))
        if i == 0:
            an_area_0 = an_area
            sum_area_0 = sum(bunch_area)
        an_area_list.append(an_area)
        area_list_of_lists.append(bunch_area)
    try:
        print an_area_list[-1]/an_area_list[0], sum(area_list_of_lists[-1])/sum(area_list_of_lists[0])
    except Exception:
        print area_list_of_lists[0]
        print area_list_of_lists[-1]
        sys.excepthook(*sys.exc_info())
    sys.stdout.flush()
    return {
      "areas":areas,
      "z_list":[bunch[0]['z'] for bunch in bunch_list],
      "an_area_list":an_area_list, # this is calculated differently; cross-check
      "area_list_of_lists":area_list_of_lists,
      "delta":delta,
      "step_size":tracking.step_size,
      "physics_processes":tracking.physics_processes,
      "seed":[bunch[0].dict_from_hit() for bunch in bunch_list],
    }


class write_data(object):
    def __init__(self, data):
        if write_data.fout == None: # give user a chance to back out before overwriting!
            print "Opening output file"
            write_data.fout = open("single_tracking.json", "w")
        print >> write_data.fout, json.dumps(data)

    fout = None

def main():
    analysis.SingleTracking.max_track_length = 12011.
    analysis.SingleTracking.step_size = 10.
    tracking = analysis.SingleTracking("geometries/cd_step_frozen_53_1.dat")

    for a_delta in [1.]:
        variables = ['x', 'px', 'y', 'py']#, 't', 'energy']
        delta = dict(zip(variables, [a_delta for var in variables]))
        if 't' in variables:
            delta['t'] = 0.01 # 50 ps
        if 'energy' in variables:
            delta['energy'] = 0.1 # 50 ps
        if 'px' in variables:
            delta['px'] = 0.1 # 0.1 MeV/c
        if 'py' in variables:
            delta['py'] = 0.1 # 0.1 MeV/c

        for x in [i/0.1 for i in range(0, 21, 1)]:
            for px in [i/1. for i in range(0, 21, 1)]:
                data = do_one(tracking, get_hit(x, 0, -6000.1, 0., px, 0., 140.), delta)
                write_data(data)

if __name__ == "__main__":
    main()
    print "Finished"

