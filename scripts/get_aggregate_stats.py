import os
import holographic as hl
import ScriptHelper as Sh

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01
folder = 'img/'

fn = []
for _, _, fn in os.walk(folder):
    break

fn = [os.path.join(folder, f) for f in fn]

lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, *fn)
partitions = {mode: hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode) for mode in range(1, 3+1)}

params = {'big_m': big_m, 'small_m': small_m,
          'big_n': big_n, 'sigma': sigma}
data = {'lamda': lamda, 'psi': psi,
        'partitions': partitions}

import pprint
print 'Lambdas: ', pprint.pprint(lamda)

Sh.save_data('aggregate_statistics', params, data)
print 'Saved (with params: {})'.format(params)
