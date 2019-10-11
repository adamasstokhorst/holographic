import pickle
import itertools
import collections
import holographic as hl

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

use_aggregate = True
image_fn = ''
mode = 1

if use_aggregate:
    with open('aggregate_statistics', 'r') as f:
        d = pickle.load(f)
        lamda, psi = d['lamda'], d['psi']
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
else:
    lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, 'img/' + image_fn)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)

baseline = sum(lamda)
memo = {}
result = []

for ell in range(1, big_n+1):
    best_sum = 0
    for subset in itertools.combinations(range(big_n), ell):
        subspace_counter = collections.Counter()
        for i in subset:
            subspace_counter.update(partitions[i])
        sum_p = sum([hl.statistic.zeta(x, y, lamda, sigma, memo) for (x, y) in subspace_counter.most_common()])
        best_sum = sum_p if sum_p > best_sum else best_sum
    result.append(baseline - best_sum)

fnc = image_fn.split('.')[0]
with open('modeanalysis_{}_mode{}'.format('aggregate' if use_aggregate else fnc, mode), 'w') as f:
    pickle.dump(result, f)
