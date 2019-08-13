import os
import pickle
import holographic as hl

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
partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda)

with open('aggregate_statistics', 'w') as f:
    pickle.dump({'lamda': lamda, 'psi': psi, 'partitions': partitions,
                 'big_m': big_m, 'small_m': small_m,
                 'big_n': big_n, 'sigma': sigma}, f)
