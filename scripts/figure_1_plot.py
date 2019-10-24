import math
import pickle
from matplotlib import pyplot

# Adjustable parameters
big_m = 64
sigma = 0.01

with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)
    lamda, _ = d['lamda'], d['psi']
# lamda = [0.8**i for i in range(big_m)]

harmonic_mean = sum([1.0 / lm for lm in lamda]) / big_m
rho = [harmonic_mean - 1.0 / lm for lm in lamda]

b1 = big_m * sigma * (1.0 / lamda[-1] - harmonic_mean)
b2 = big_m * sigma * (harmonic_mean - 1.0 / lamda[0]) / (big_m - 1)
big_k = math.ceil(max(b1, b2))
km = 1.0 * big_k / big_m

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)

fig.set_size_inches(12, 9)

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
# axes.set_ylabel('[insert y-label here]', fontsize=24)
# axes.set_xlabel('[insert x-label here]', fontsize=24)
# axes.set_title('[insert title here]', fontsize=32)
pyplot.savefig('rho_plot.png')
pyplot.show()
