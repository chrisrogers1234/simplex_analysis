# To run, do:
# Generates a field map
python make_field_map.py --configuration_file config.py

# Test for scipy
python -c 'import scipy' || ( echo "FATAL - SciPy not installed"; exit 1; )

# Runs tracking; this takes about 10 minutes on my desktop PC. Requires 
# additional SciPy python library.
python single_tracking.py

# Generates plots - the last three plots in the slides at
# http://micewww.pp.rl.ac.uk/projects/analysis/wiki/PC-2016-01-28-optics
python plot_single_tracking.py --configuration_file config.py 
