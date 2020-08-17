"""
Plots the eigenvalues for each image in a particular directory, and then plots
the aggregate eigenvalues on top.
"""


import os
import holographic as hl
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

# --- PARAMETERS THAT MAY BE CHANGED ---
# image files to use, leave empty to use all
files = []  # e.g. ['img/dragon.png', 'img/bratan.jpg']
folder = 'img/'

# parameters
big_m = 64

# --- END OF PARAMETERS, BEGIN CODE ---
all_fns = []
for _, _, all_fns in os.walk(folder):
    break

all_fns = [os.path.join(folder, f) for f in all_fns]
if files:
    fns = [f for f in all_fns if f in files]
else:
    fns = all_fns

fig, axes = pyplot.subplots(1)
fig.set_size_inches(10, 6.5)
fig.set_dpi(200)

for i, fn in enumerate(fns):
    print 'Processing {}...'.format(fn)
    lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
    color = pyplot.cm.get_cmap('viridis', len(fns))(i)
    axes.semilogy(range(1, big_m+1), lamda, label='.'.join(fn.split('/')[-1].split('.')[:-1]), color=color, linestyle='-')
    
print 'Calculating aggregate statistics...'
lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, *all_fns)
axes.semilogy(range(1, big_m+1), lamda, label='aggregate', color='black', linestyle='-', linewidth=2.5)

axes.grid(True, linestyle='dotted')
axes.set_ylabel(r'(Log) $\lambda_j$ values', fontsize=28)
axes.set_xlabel(r'$j$', fontsize=24)
axes.set_title(r"""\Huge Lambda plots for various images
                   \Large $\left ( M={} \right )$""".format(big_m))
axes.legend(fontsize=8, ncol=5)
pyplot.savefig('lambda_plots.eps')

print 'Saved to lambda_plots.eps'
