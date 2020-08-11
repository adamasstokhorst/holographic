"""
Plots the MSE graphs for individual images using various parameters, as chosen
by the user -- the modes, recovery procedure, and lambda profiles. The graphs
will be overlaid in one image. This will not save the recovered images.
"""

import numpy
import itertools
import random

import holographic as hl
import ScriptHelper as Sh

from matplotlib import pyplot

# --- PARAMETERS THAT MAY BE CHANGED ---
big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

fn = 'img/dragon.png'
img_mode = 'L'

# --- END OF PARAMETERS, BEGIN CODE ---
print 'Choose lines to display:'
print '(mode 1, 2, 3 -- as binary string)'
print '(e.g. 011 will display mode 2 plot and mode 3 plot)'
print '>',
choice = raw_input()
selector = [c == '1' for c in choice]
modes = list(itertools.compress(range(1, 4), selector))

print '(recovery procedure: build-up, randomized)'
print '>',
choice = raw_input()
selector = [c == '1' for c in choice]
do_buildups = list(itertools.compress([True, False], selector))

print '(lambda profile: image-specific, aggregate, line, grid)'
print '>',
choice = raw_input()
selector = [c == '1' for c in choice]
which_stats = list(itertools.compress(['image', 'aggr', 'line', 'grid'], selector))
ls = {'image': '--',
      'aggr': '-',
      'line': ':',
      'grid': '-.'}

formats = Sh.get_fname(fn), big_m, small_m, big_n, sigma
title_text = (r"\Huge MSE plot for \texttt{{{}}} on various parameters" "\n"
              r"\Large $\left ( M={},m={},N={},\sigma^2_n={} \right )$").format(*formats)

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

ctr = 0
total = len(modes) * len(do_buildups)
for mode, do_buildup, stats_to_use in itertools.product(modes, do_buildups, which_stats):
    simul_mode = 'build-up' if do_buildup else 'random'
    fn_prefix = 'BUILDUP' if do_buildup else 'SINGLE'
    print 'Simulating {} recovery on {}'.format(simul_mode, fn)
    print '  Parameters: M={}, m={}, N={}, sigma^2={} on mode {}'.format(big_m, small_m, big_n, sigma, mode)
    print '  Using {} statistics...'.format('aggregate' if stats_to_use == 'aggr' else stats_to_use)

    if stats_to_use == 'image':
        # using image-specific statistics
        lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
        partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
    elif stats_to_use == 'aggr':
        # using aggregate statistics
        d = Sh.load_data('aggregate_statistics', {'big_m': big_m,
                                                  'small_m': small_m,
                                                  'big_n': big_n,
                                                  'sigma': sigma})
        lamda, psi, partitions = d['lamda'], d['psi'], d['partitions'][mode]
    elif stats_to_use == 'grid':
        lamda, psi = hl.statistic.get_lp_lambda(1, big_m)
        partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
    elif stats_to_use == 'line':
        lamda, psi = hl.statistic.get_lp_lambda(2, big_m)
        partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
    else:
        raise ValueError('unrecognized statistic parameter. (got {})'.format(stats_to_use))

    if do_buildup:
        sp = random.sample(range(big_n), big_n)

    x_points = []
    y_points = []

    print 'Processing ell =',
    for i in xrange(1, big_n + 1):
        print i,
        image_in = hl.ImageHandler(fn, big_m, mode='r', color_mode=img_mode)

        if do_buildup:
            g = hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, lost_space=sp[i:])
        else:
            g = hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=i)

        errors = []
        for i_packet, o_packet in g:
            for comp_pair in zip(i_packet, o_packet):
                errors.append(hl.helpers.mean_squared_error(*comp_pair))

        x_points.append(i)
        y_points.append(numpy.mean(errors))

    color = pyplot.cm.get_cmap('viridis', total)(ctr / len(which_stats))
    axes.plot(x_points, y_points, label='mode {} ({}, {})'.format(mode, simul_mode, stats_to_use), color=color, linestyle=ls[stats_to_use])
    ctr += 1
    print

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(title_text)
axes.legend()
pyplot.savefig('single_image_composite_plot.svg')

print 'Saved to single_image_composite_plot.svg'
