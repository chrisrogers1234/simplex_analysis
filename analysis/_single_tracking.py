import json
import sys
import math
import copy
import os

import ROOT
import numpy

from Configuration import Configuration
from xboa.tracking import MAUSTracking
from xboa.algorithms.closed_orbit import EllipseClosedOrbitFinder
from xboa.algorithms.closed_orbit import EllipseClosedOrbitFinderIteration
from xboa.algorithms.tune import FFTTuneFinder
from xboa.hit import Hit
from xboa.bunch import Bunch
import xboa.common as common
import maus_cpp.globals
import maus_cpp.field
import maus_cpp.mice_module
import maus_cpp.polynomial_map
from _delaunay_wrapper import DelaunayWrapper

class SingleTracking:
    def __init__(self, geometry):
        self.maus = self.get_maus(geometry)
        self.delaunay_wrapper = None

    def get_maus(self, geometry):
        dc = Configuration().getConfigJSON()
        py_dc = json.loads(dc)
        py_dc["simulation_geometry_filename"] = geometry
        py_dc["verbose_level"] = 5
        py_dc["maximum_number_of_steps"] = 1000000
        py_dc["max_track_length"] = self.max_track_length
        py_dc["max_step_length"] = self.step_size
        py_dc["geant4_visualisation"] = False
        py_dc["keep_steps"] = False
        py_dc["particle_decay"] = False
        py_dc["physics_processes"] = self.physics_processes
        if maus_cpp.globals.has_instance():
            maus_cpp.globals.death()
        maus_cpp.globals.birth(json.dumps(py_dc))
        return MAUSTracking(json.dumps(py_dc))


    def track(self, centre_hit, delta):
        primary_list = [centre_hit]
        for key, value in delta.iteritems():
            hit = centre_hit.deepcopy()
            hit[key] += value
            hit.mass_shell_condition('pz')
            primary_list.append(hit)
        # qhull needs 8 particles for some reason - so make an extra one
        hit = centre_hit.deepcopy()
        for key, value in delta.iteritems():
            hit[key] += value
        hit.mass_shell_condition('pz')
        primary_list.append(hit)
        bunch = Bunch.new_from_hits(primary_list)
        return self.track_bunch(bunch)

    def track_bunch(self, bunch):
        primary_list = bunch.hits()
        hit_list_of_lists = self.maus.track_many(primary_list)
        # hit_list_of_lists is sliced by primary; we want to slice by station
        n_events = len(primary_list)
        # we take the min here to stop 
        n_stations = min([len(hit_list) for hit_list in hit_list_of_lists])
        i_list = range(n_events)
        j_list = range(n_stations)
        hit_lost_if_losts = [[hit_list_of_lists[i][j] for i in i_list] for j in j_list]
        # convert to a bunch
        bunch_list = [Bunch.new_from_hits(hit_list) for hit_list in hit_lost_if_losts]
        self.bunch_list = bunch_list
        return bunch_list

    def delaunay(self, variables):
        self.delaunay_wrapper = DelaunayWrapper(self.bunch_list[0], variables)
        areas = []
        for i, bunch in enumerate(self.bunch_list):
            try:
                areas.append(self.delaunay_wrapper.get_areas(bunch))
            except Exception as exc:
                if type(exc) == type(RuntimeError()):
                    raise
                print "Delaunay failed at bunch id", i, "z=", bunch[0]['z'], "with", len(bunch), "particles"
                sys.excepthook(*sys.exc_info())
                
        return areas

    def areas_low_triangle(self, variables):
        areas = [delaunay.get_areas(bunch) for bunch in self.bunch_list]
        return areas

    max_track_length = 8011.
    step_size = 10.
    physics_processes = "none"


