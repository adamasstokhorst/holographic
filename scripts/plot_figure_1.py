import math
import pickle
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)

params = [sorted(list(p)) for p in d.keys()]

print 'Choose parameter to plot:'
for i, c in enumerate(params):
    print '  {}: {}'.format(i, c)
print '>',
choice = int(raw_input())
param = params[choice]
p_dict = dict(param)

big_m = p_dict['big_m']
sigma = p_dict['sigma']
lamda = d[frozenset(param)]['lamda']
# lamda = [0.8**i for i in range(big_m)]

harmonic_mean = sum([1.0 / lm for lm in lamda]) / big_m
rho = [harmonic_mean - 1.0 / lm for lm in lamda]

b1 = big_m * sigma * (1.0 / lamda[-1] - harmonic_mean)
b2 = big_m * sigma * (harmonic_mean - 1.0 / lamda[0]) / (big_m - 1)
big_k = math.ceil(max(b1, b2))
km = 1.0 * big_k / big_m

fig, axes = pyplot.subplots(1)
fig.set_size_inches(8, 6)
fig.set_dpi(200)

axes.plot(range(1, big_m+1), rho, color='black', linestyle='-')

xlim, ylim = pyplot.xlim(), pyplot.ylim()
axes.plot([xlim[0], xlim[-1]], [km, km], color='grey', linestyle='--')
pyplot.xlim(xlim)
pyplot.ylim(ylim)

axes.annotate('$\\frac{K}{M}$',
              xy=(xlim[-1], km), xycoords='data',
              xytext=(5, 0), textcoords='offset points', size=20,
              horizontalalignment='left', verticalalignment='center')

axes.grid(True, linestyle='dotted')
axes.set_ylabel(r'$\rho (j)$', fontsize=24)
axes.set_yticks([])
axes.set_xlabel('$j$', fontsize=24)
axes.set_xticks(range(0, big_m+1, 8))
pyplot.savefig('rho_plot.png')
