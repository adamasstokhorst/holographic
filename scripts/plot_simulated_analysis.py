"""
Plots the result of `simulated_analysis.py`.
"""

import collections
import itertools
import os
import pickle
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

data_path = 'plot_data/'

fns = []
for _, _, fns in os.walk(data_path):
    break

fns = [os.path.join(data_path, fn) for fn in fns if fn != 'README.md']

key_list = []
for fn in fns:
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)
        key_list.extend(raw_data.keys())

counts = collections.Counter(key_list).most_common()

print 'Choose parameter to plot:'
for i, c in enumerate(counts):
    print '  {}: {} ({} entries)'.format(i, list(c[0]), c[1])
print '>',
choice = int(raw_input())
param = counts[choice][0]

print 'Choose lines to display:'
print '(image-specific, aggregate, line, grid -- as binary string)'
print '(e.g. 1001 will display image-specific plot and grid-lambda plot)'
print '>',
choice = raw_input()
selector = [c == '1' for c in choice]
keys = ['img', 'aggregate', 'line', 'grid']
ls = {'img': '--',
      'aggregate': '-',
      'line': ':',
      'grid': '-.'}

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

for i, fn in enumerate(fns):
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)
    
    if param not in raw_data:
        continue
    
    data = raw_data[param]

    color = pyplot.cm.get_cmap('viridis', len(fns))(i)
    for k in itertools.compress(keys, selector):
        axes.plot(data['x'], data[k]['avg'], label='{} ({})'.format(data['label'], k), color=color, linestyle=ls[k])

p = dict(param)
big_m, small_m, big_n, sigma = p['big_m'], p['small_m'], p['big_n'], p['sigma']

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(r"""\Huge Average MSE plots for various images
                   \Large $\left ( M={},m={},N={},\sigma^2_n={} \right )$""".format(big_m, small_m, big_n, sigma))
axes.legend()
pyplot.savefig('aggregate_mse_plot.eps')

print 'Saved to aggregate_mse_plot.eps'

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

for i, fn in enumerate(fns):
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)
    
    if param not in raw_data:
        continue
    
    data = raw_data[param]

    color = pyplot.cm.get_cmap('viridis', len(fns))(i)
    for k in itertools.compress(keys, selector):
        axes.plot(data['x'], data[k]['var'], label='{} ({})'.format(data['label'], k), color=color, linestyle=ls[k])

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Variance of MSE', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(r"""\Huge Variance of MSE plots for various images
                   \Large $\left ( M={},m={},N={},\sigma^2_n={} \right )$""".format(big_m, small_m, big_n, sigma))
axes.legend()
pyplot.savefig('aggregate_var_mse_plot.eps')

print 'Saved to aggregate_var_mse_plot.eps'
