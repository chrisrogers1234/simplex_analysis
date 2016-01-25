simulation_reference_particle = {
    "random_seed": 0,
    "energy":226.,
    "particle_id":-13,
    "time": 0.0,
    "position":{"x":0.0, "y":0.0, "z":-3472.001},
    "momentum":{"x":0.0, "y":0.0, "z":1.0}
}
simulation_geometry_filename = "geometries/cd_step_frozen_53_1.dat"
verbose_level = 1
keep_tracks = True

spill_generator_number_of_spills = 1

beam = {
  "particle_generator":"file",
  "beam_file":"tmp/for003.dat",
  "beam_file_format":"icool_for003",
  "file_particles_per_spill":1,
  "random_seed":0,
}

physics_processes = "none"
particle_decay = False


