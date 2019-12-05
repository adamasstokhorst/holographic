import os
import pickle
import collections
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

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

for i, fn in enumerate(fns):
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)
    
    if param not in raw_data:
        continue
    
    data = raw_data[param]

    color = pyplot.cm.get_cmap('brg', len(fns))(i)
    axes.semilogy(data['x'], data['y'], label=data['label'], color=color, linestyle='-')
    axes.semilogy(data['x'], data['y2'], label=data['label'] + ' (sp)', color=color, linestyle='--')

param = dict(param)
big_m, small_m, big_n, sigma = param['big_m'], param['small_m'], param['big_n'], param['sigma']

axes.grid(True, linestyle='dotted')
axes.set_ylabel('(Log) Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title(r"""\Huge Aggregate MSE plots for various images
                   \Large $\left ( M={},m={},N={},\sigma^2_n={} \right )$""".format(big_m, small_m, big_n, sigma))
axes.legend()
pyplot.savefig('aggregate_mse_plot.png')

print 'Saved to aggregate_mse_plot.png'
