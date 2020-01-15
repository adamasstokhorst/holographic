import os
import pickle
import collections
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

fns = []
for _, _, fns in os.walk('.\\'):
    break

fns = [fn for fn in fns if fn.startswith('modeanalysis')]
fnset = [fn.split('_')[1] for fn in fns if 'aggregate' not in fn]

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

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

for fn in fns:
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)

    if param not in raw_data:
        continue

    data = raw_data[param]['data']
    name = raw_data[param]['label']

    color = 'black' if name == 'aggregate' else pyplot.cm.get_cmap('viridis', len(fnset))(fnset.index(name))

    for d in data:
        mode = d['mode']
        if mode <= 3:
            label = '{} (mode {})'.format(name, mode)
            lw = 1
            continue  # comment this line to unhide mode 1/2/3 plots
        else:
            label = '{} (thr. best)'.format(name)
            lw = 2
        linestyle = '-.' if mode == 1 else '--' if mode == 2 else ':' if mode == 3 else '-'

        axes.plot(d['x'], d['y'], label=label, color=color, linestyle=linestyle, linewidth=lw)

param = dict(param)
big_m, small_m, big_n, sigma = param['big_m'], param['small_m'], param['big_n'], param['sigma']

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(r"""\Huge Calculated best case MSE plots for various data
                   \Large $\left ( M={},m={},N={},\sigma^2_n={} \right )$""".format(big_m, small_m, big_n, sigma))
axes.legend()
pyplot.savefig('mode_analysis_plot.png')

print 'Saved to mode_analysis_plot.png'
