import os
import pickle
from matplotlib import pyplot

fns = []
for _, _, fns in os.walk('.\\'):
    break

fns = [fn for fn in fns if fn.startswith('modeanalysis')]
fnset = list(set([fn.split('_')[1] for fn in fns if 'aggregate' not in fn]))

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)

for fn in fns:
    with open(fn, 'r') as f:
        data = pickle.load(f)

    color = 'black' if data['label'] == 'aggregate' else pyplot.cm.get_cmap('brg', len(fnset))(fnset.index(data['label']))
    label = '{} (mode {})'.format(data['label'], data['mode'])
    mode = data['mode']
    linestyle = '-.' if mode == 1 else '--' if mode == 2 else ':'
    if data['label'] == 'aggregate':
        axes.plot(data['x'], data['y'], label=label, color=color, linestyle=linestyle, linewidth=2)
    else:
        axes.plot(data['x'], data['y'], label=label, color=color, linestyle=linestyle)

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title('Calculated best case MSE plots for various data', fontsize=32)
axes.legend()
pyplot.savefig('mode_analysis_plot.png')
pyplot.show()
