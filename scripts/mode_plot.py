import os
import pickle
from matplotlib import pyplot
import holographic as hl

fns = []
for _, _, fns in os.walk('.\\'):
    break

fns = [fn for fn in fns if fn.startswith('modeanalysis')]
fnset = list(set([fn.split('_')[1] for fn in fns if 'aggregate' not in fn]))

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)

prev_param = None

for fn in fns:
    with open(fn, 'r') as f:
        raw_data = pickle.load(f)

    data = raw_data['data']
    name = raw_data['label']
    param = raw_data['param']
    
    if param != prev_param and prev_param is not None:
        print 'WARNING: parameter is not shared between all data'
    
    color = 'black' if name == 'aggregate' else pyplot.cm.get_cmap('brg', len(fnset))(fnset.index(name))
    
    for d in data:
        mode = d['mode']
        label = '{} (mode {})'.format(name, mode)
        linestyle = '-.' if mode == 1 else '--' if mode == 2 else ':' if mode == 3 else '-'
        
        axes.plot(d['x'], d['y'], label=label, color=color, linestyle=linestyle)

# add theoretical best possible MSE reduction
big_m, big_n, small_m, sigma = param['big_m'], param['big_n'], param['small_m'], param['sigma']
result = []
with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)
    lamda, _ = d['lamda'], d['psi']
for ell in range(1, big_n+1):
    partitions = hl.statistic.calculate_partition(big_m, ell, small_m, sigma, lamda, mode=2)
    big_l = max([max(p) for p in partitions])
    print big_l, partitions
    result.append(big_m * sigma / (1.0 * ell * small_m / big_m + 1.0 * sigma * sum([1.0 / lamda[i] for i in range(big_l)]) / big_l))
axes.plot(range(1, big_n+1), result, label='theoretical best', color='black', linestyle='-', linewidth=1)

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title('Calculated best case MSE plots for various data', fontsize=32)
axes.legend()
pyplot.savefig('mode_analysis_plot.png')
pyplot.show()
