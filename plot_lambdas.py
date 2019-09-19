import os
import holographic as hl
from matplotlib import pyplot

big_m = 256
# small_m = 8
# big_n = 8
# sigma = 0.01
folder = 'img/'

fns = []
for _, _, fns in os.walk(folder):
    break

fns = [os.path.join(folder, f) for f in fns]

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)

for i, fn in enumerate(fns):
    print 'Processing {}...'.format(fn)
    lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
    color = pyplot.cm.get_cmap('Spectral', len(fns))(i)
    axes.semilogy(range(1, big_m+1), lamda, label='.'.join(fn.split('/')[-1].split('.')[:-1]), color=color, linestyle='-')
    
print 'Calculating aggregate statistics...'
lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, *fns)
axes.semilogy(range(1, big_m+1), lamda, label='aggregate', color='black', linestyle='-', linewidth=5)

axes.grid(True, linestyle='dotted')
axes.set_ylabel('Lambda values', fontsize=28)
axes.set_xlabel(r'$i$', fontsize=24)
axes.set_title('Lambda Plots for Images when M=256', fontsize=32)
axes.legend(fontsize=8, ncol=5)
pyplot.savefig('lambda_plots_M256.png')
pyplot.show()
