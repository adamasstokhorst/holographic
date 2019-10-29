import os
import pickle
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

data_path = 'plot_data/'

fns = []
for _, _, fns in os.walk(data_path):
    break

fns = [os.path.join(data_path, fn) for fn in fns]

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)

for i, fn in enumerate(fns):
    with open(fn, 'rb') as f:
        data = pickle.load(f)

    color = pyplot.cm.get_cmap('brg', len(fns))(i)
    axes.semilogy(data['x'], data['y'], label=data['label'], color=color, linestyle='-')
    axes.semilogy(data['x'], data['y2'], label=data['label'] + ' (sp)', color=color, linestyle='--')

axes.grid(True, linestyle='dotted')
axes.set_ylabel('(Log) Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.set_title('Aggregate MSE plots for various images', fontsize=32)
axes.legend()
pyplot.savefig('aggregate_mse_plot.png')
pyplot.show()
