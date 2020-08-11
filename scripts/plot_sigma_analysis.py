"""
Plots the theoretical best-case recovery for a particular image, while varying
the noise, as calculated by `theoretical_analysis.py`.
"""

import collections
import pickle
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

im_name = raw_input('Image data to plot: ')
fn = 'modeanalysis_' + im_name

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

key_list = []
with open(fn, 'r') as f:
    raw_data = pickle.load(f)
    key_list += [frozenset([p for p in k if p[0] != 'sigma']) for k in raw_data.keys()]

counts = collections.Counter(key_list).most_common()

print 'Choose parameter to plot:'
for i, c in enumerate(counts):
    print '  {}: {} ({} entries)'.format(i, list(c[0]), c[1])
print '>',
choice = int(raw_input())
sub_param = counts[choice][0]
total = counts[choice][1]

with open(fn, 'r') as f:
    raw_data = pickle.load(f)

ctr = 0
for param in sorted([sorted(list(x)) for x in raw_data.keys()]):
    param = frozenset(param)
    if not sub_param <= param:
        continue

    data = raw_data[param]['data']
    sigma = dict(param)['sigma']

    color = pyplot.cm.get_cmap('viridis', total)(ctr)

    for d in data:
        mode = d['mode']
        if mode <= 3:
            label = None  # r'$\sigma^2_n={}$ (mode {})'.format(sigma, mode)
            lw = 1
        else:
            label = r'$\sigma^2_n={}$'.format(sigma)  # r'$\sigma^2_n={}$ (thr. best)'.format(sigma)
            lw = 2
        linestyle = '-.' if mode == 1 else '--' if mode == 2 else ':' if mode == 3 else '-'

        axes.plot(d['x'], d['y'], label=label, color=color, linestyle=linestyle, linewidth=lw)

    ctr += 1

param = dict(sub_param)
big_m, small_m, big_n = param['big_m'], param['small_m'], param['big_n']

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(r"""\Huge Calculated best case MSE plots for \texttt{{{}}}
                   \Large $\left ( M={},m={},N={} \right )$""".format(im_name, big_m, small_m, big_n))
axes.legend()
pyplot.savefig('sigma_analysis_plot.svg')

print 'Saved to sigma_analysis_plot.svg'
