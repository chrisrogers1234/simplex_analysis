import os
import subprocess
import json
import operator

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

class DelaunayWrapper:
    def __init__(self, target_bunch, variables):
        # regularise the bunches
        self.target_bunch = target_bunch
        self.variables = variables
        self.triangulation = None
        self.bunch_delaunay()

    def bunch_delaunay(self):
        position_array = [[hit[var] for var in self.variables] \
                                   for hit in self.target_bunch]
        position_array = numpy.array(position_array)
        self.triangulation = Delaunay(position_array)

    def _get_this_hit_list(self, bunch):
        hits = bunch.hits()
        event_index = [(hit['spill'], hit['event_number'], hit['particle_number']) for hit in hits] 
        hit_map = dict(zip(event_index, hits))
        this_hit_list = []
        for target_hit in self.target_bunch.hits():
            index = (target_hit['spill'], target_hit['event_number'], target_hit['particle_number'])
            
            if index not in hit_map:
                this_hit_list.append(None)
            else:
                hit = hit_map[index]
                this_hit_list.append([hit[var] for var in self.variables])
        return this_hit_list

    def get_an_area(self, bunch, index, coordinate_list = None):
        #vertices index a hit in bunch
        if coordinate_list == None:
            coordinate_list = self._get_this_hit_list(bunch)
        vertices_index = self.triangulation.simplices[index]
        vertices_coords = [coordinate_list[vertex] for vertex in vertices_index]
        if None in vertices_coords:
            return None
        area = xboa.bunch.weighting._hull_content._tile_content((vertices_index,
                                                               vertices_coords))
        return area

    def get_areas(self, bunch):
        """
        Get the areas of tiles defined by delaunay triangulation
        - bunch: bunch for which tile areas should be calculated
        Calculates a list of triangle areas. The triangles are defined by the 
        initial triangulation of target_bunch. If a hit does not appear in
        bunch, but does appear in target_bunch, then no area can be calculated
        for triangles that have that hit as a vertex and an area of None will
        be given.
         
        Returns a list of areas (or None).
        """
        coordinate_list = self._get_this_hit_list(bunch)
        area_list = [self.get_an_area(bunch, index, coordinate_list) for index in \
                                       range(len(self.triangulation.simplices))]
        return area_list

