"""
Plots the ordered eigenvalues for various metrics, including the aggregate
ensemble. Run `get_aggregate_stats.py` with the desired parameters first.
"""

import holographic as hl
import ScriptHelper as Sh
from matplotlib import pyplot

pyplot.rc('text', usetex=True)
pyplot.rc('font', family='Palatino')

# --- PARAMETERS THAT MAY BE CHANGED ---
big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

# --- END OF PARAMETERS, BEGIN CODE ---
lamda_grid, _ = hl.statistic.get_lp_lambda(1, big_m)
lamda_line, _ = hl.statistic.get_lp_lambda(2, big_m)

params = {'big_m': big_m,
          'small_m': small_m,
          'big_n': big_n,
          'sigma': sigma}
d = Sh.load_data('aggregate_statistics', params)
lamda_agg, _ = d['lamda'], d['psi']

fig, axes = pyplot.subplots(1)
fig.set_size_inches(9, 6)
fig.set_dpi(200)

cmap = pyplot.cm.get_cmap('brg', 3)
axes.semilogy(range(1, big_m+1), lamda_agg, label='aggregate', color=cmap(0), linestyle='-')
axes.semilogy(range(1, big_m+1), lamda_grid, label='manhattan', color=cmap(1), linestyle='-')
axes.semilogy(range(1, big_m+1), lamda_line, label=r'$\ell_2$', color=cmap(2), linestyle='-')

axes.grid(True, linestyle='dotted')
axes.set_ylabel(r'(Log) $\lambda_j$ values', fontsize=28)
axes.set_xlabel(r'$j$', fontsize=24)
axes.set_title(r"""\Huge Lambda plots for different metrics
                   \Large $\left ( M={} \right )$""".format(big_m))
axes.legend(fontsize=8, ncol=5)
pyplot.savefig('lambda_compare_plots.svg')

print 'Saved to lambda_compare_plots.svg'
