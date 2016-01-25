#!/usr/bin/env bash
# Test for scipy
python -c 'import MAUS'
if [[ $? != 0 ]]; then
    echo "FATAL - MAUS not installed"
    exit 1
fi
python -c 'import scipy'
if [[ $? != 0 ]]; then
    echo "FATAL - SciPy not installed"
    exit 1
fi
python -c 'import xboa; print xboa.__version__'
if [[ $? != 0 ]]; then
    echo "FATAL - xboa version should be at least 0.17.d"
    exit 1
fi


# To run, do:
# Generates a field map
python make_field_map.py --configuration_file config.py

# Runs tracking; this takes about 10 minutes on my desktop PC. Requires 
# additional SciPy python library.
python single_tracking.py

# Generates plots - the last three plots in the slides at
# http://micewww.pp.rl.ac.uk/projects/analysis/wiki/PC-2016-01-28-optics
python plot_single_tracking.py --configuration_file config.py 
