import os
import pickle
from matplotlib import pyplot

fns = []
for _, _, fns in os.walk('/'):
    break

fns = [os.path.join(data_path, fn) for fn in fns if fn.startswith('modeanalysis')]

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)
i = 0

for fn in fns:
    with open(fn, 'rb') as f:
        data = pickle.load(f)

    color = pyplot.cm.get_cmap('brg', len(fns))(i)
    label = '{} (mode {})'.format(data['label'], data['mode'])
    if data['label'] == 'aggregate':
        axes.plot(data['x'], data['y'], label=label, color='black', linestyle='-', linewidth=5)
    else:
        axes.plot(data['x'], data['y'], label=label, color=color, linestyle='-')
        i += 1

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title('Calculated best case MSE plots for various data', fontsize=32)
axes.legend()
pyplot.savefig('mode_analysis_plot.png')
pyplot.show()
