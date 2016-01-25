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

from _delaunay_wrapper import DelaunayWrapper

class MultiTracking:

    def tracking(self, n_particles):
        #hit_list = []
        #for i, amplitude in enumerate([1.]+[i*10. for i in range(1, 11)]):
        #    hit_list += self.make_bunch(amplitude)
        common.substitute("config_gaussian.in", "tmp/config.py",
            {
                "__n_particles__":n_particles,
            })

        #bunch = Bunch.new_from_hits(hit_list)
        #bunch.hit_write_builtin("icool_for003", "tmp/for003.dat")
        sim = os.path.expandvars("${MAUS_ROOT_DIR}/bin/simulate_mice.py")
        proc = subprocess.Popen(['python', sim, '--configuration_file', 'tmp/config.py'])
        proc.wait()

    def plot_areas(self, areas_us, areas_ds):
        assert(len(areas_us) == len(areas_ds))
        # remove None items from the list (failed to calculate area)
        areas = zip(areas_us, areas_ds)
        areas = [item for item in areas if item[0] != None and item[1] != None]
        areas_us = [item[0] for item in areas]
        areas_ds = [item[1] for item in areas]
        # remove residuals
        areas_res = [item[1]-item[0] for item in areas]
        for i in range(3):#len(areas_us)):
            print i, str(round(areas_us[i])).ljust(10), str(round(areas_ds[i])).ljust(10), areas_res[i]
        # plots
        canvas = common.make_root_canvas("content")
        n_bins = 100# max(int((len(bunch_us)/10)**0.5), 10)

        hist_us = common.make_root_histogram("Upstream", areas_us, "cell content [mm MeV/c]", n_bins, xmin=-5000.0, xmax=5000.0)
        hist_us.SetLineColor(2)
        hist_us.Draw()
        hist_ds = common.make_root_histogram("Downstream", areas_ds, "cell content [mm MeV/c]", n_bins, xmin=-5000.0, xmax=5000.0)
        hist_ds.SetLineColor(4)
        hist_ds.Draw("SAME")
        hist_res = common.make_root_histogram("Residuals", areas_res, "cell content [mm MeV/c]", n_bins)
        hist_res.Draw("SAME")


    def analysis(self):
        print "Loading data"
        bunch_list = Bunch.new_list_from_read_builtin('maus_root_virtual_hit', 'maus_output.100.root')
        bunch_list = [bunch for bunch in bunch_list if bunch.bunch_weight() > 10 and bunch[0]['z'] < 3472.001]
        print len(bunch_list)
        delaunay = DelaunayWrapper(bunch_list[0], ['x', 'px', 'y', 'py', 't', 'energy'])
        areas_0 = delaunay.get_areas(bunch_list[0])
        areas_1 = delaunay.get_areas(bunch_list[1])
        self.plot_areas(areas_0, areas_1)

    def apertures(self):
        cell_length = 2000.
        sol_offset = 600.
        ss_length = 2923.-259.
        ss_start = +124.+3200+sol_offset+cell_length/2.
        ss_end = ss_start+ss_length
        return [
          {"name":"ss", "colour":2, "radius":200., "start_z":-ss_start, "end_z":-ss_end},
          {"name":"ss", "colour":2, "radius":200., "start_z":+ss_start, "end_z":+ss_end},
          {"name":"fc", "colour":4, "radius":210., "start_z":-1000.-422., "end_z":-1000.+422.},
          {"name":"fc", "colour":4, "radius":210., "start_z":+1000.-422., "end_z":+1000.+422.},
          {"name":"rf", "colour":6, "radius":210., "start_z":-501., "end_z":-499.},
          {"name":"rf", "colour":6, "radius":210., "start_z":-101., "end_z":-99.},
          {"name":"rf", "colour":6, "radius":210., "start_z":+499., "end_z":+501.},
          {"name":"rf", "colour":6, "radius":210., "start_z":+99.,  "end_z":+101.},
        ]

    def __init__(self, momentum, amplitude):
        self.p = momentum
        self.corr_a_p = 0.0
        self.m_mu = common.pdg_pid_to_mass[13]
        self.bz_us = +4.e-3
        self.beta = self.p/self.bz_us*2./common.constants['c_light']
        self.bz_ds = -4e-3
        self.scraped = {'__any__':[]}
        #self.tracking(100)
        self.analysis()

