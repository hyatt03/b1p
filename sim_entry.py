#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('cairo')
# [u'pgf', u'ps', u'Qt4Agg', u'GTK', u'GTKAgg', u'nbAgg', u'agg', u'cairo',
# u'MacOSX', u'GTKCairo', u'Qt5Agg', u'template', u'WXAgg', u'TkAgg',
# u'GTK3Cairo', u'GTK3Agg', u'svg', u'WebAgg', u'pdf', u'gdk', u'WX']


import json
import pandas as pd
import numpy as np
from cli_helper import handle_arguments, handle_constant_properties, get_data_dir
from Particles import handle_molecule_from_file
from simulation_iterator import simulation_iterator, plot_spins
from annealing import parrallel_anneal
from fourier import fourier, plot_fourier, plot_energy_spectrum, calculate_scattering_intensity, parallel_compute_scattering_intensity


def main():
    o = handle_arguments() # Getting options
    o = handle_constant_properties(o) # Append constants

    print('Opening molecule')
    particles = handle_molecule_from_file(o)

    # Create a suitable data directory
    data_dir = get_data_dir(o)

    # Save the options of this run
    with open('{}/parameters.json'.format(data_dir), 'w') as params:
        options_dict = vars(o)
        for key, value in options_dict.iteritems():
            if type(value) == type(np.array([])):
                options_dict[key] = value.tolist()

        params.writelines(json.dumps(options_dict))

    # Simulated annealing attempts to find a ground state for the system by gradually lowering the temperature.
    if o.anneal:
        print('Annealing')
        particles = parrallel_anneal(o, particles, 8)

    if o.datafile:
        print('Loading datafile')
        results = pd.read_hdf(o.datafile)
        print('Loaded {} rows'.format(len(results)))
    else:
        # Begin the main simulation phase
        print('Starting simulation')
        results = simulation_iterator(o, particles)

        # Save the raw results
        print ('Done simulating')
        filename = '{}/datafile.h5'.format(data_dir)
        results.to_hdf(filename, 'df')

        print('Saved data to {}'.format(filename))

    # Plot if needed.
    if o.should_plot_spins:
        print('Plotting spins')
        plot_spins(results, '{}/spin_plot'.format(data_dir))

    # Runs a fourier transform
    if o.fourier:
        print('Transforming results')
        # parallel_compute_scattering_intensity(o, results, particles)
        # calculate_scattering_intensity(o, results, particles)
        # total_fourier, f, energy = fourier(o, results)
        I_aa_temp, energy, frequency = fourier(o, results, particles)

        print(I_aa_temp)

        # Plot the transformed variables
        if o.should_plot_energy:
            print('Plotting transformed results')
            plot_fourier(o, '{}/energy_q0.png'.format(data_dir), I_aa_temp, frequency, energy)

        if o.should_plot_neutron:
            print('Plotting energy spectrum')
            plot_energy_spectrum(o, I_aa_temp, frequency, energy)

    return results


if __name__ == '__main__':
    main()
