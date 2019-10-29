import pickle
import itertools
import collections
import holographic as hl

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

use_aggregate = False
image_fn = 'dragon.png'

if use_aggregate:
    with open('aggregate_statistics', 'r') as f:
        d = pickle.load(f)
        lamda, _ = d['lamda'], d['psi']
else:
    lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, 'img/' + image_fn)

total_result = []

# calculate best possible MSE reduction using each partition strategy
for mode in range(1, 4+1):
    if mode <= 3:
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

        total_result.append(result)
    else:
        # mode "4" and "5" are for theoretical best with mode 1 and 2, resp.
        result_1 = []
        result_2 = []
        for ell in range(1, big_n+1):
            big_k = ell * small_m
            big_l = big_m
            zetas = [1.0 * big_k / big_l + sigma * (sum([1.0 / lm for lm in lamda[:big_l]]) / big_l - 1.0 / lamda[i]) for i in range(big_l)]
            while any([z<0 for z in zetas]):
                big_l -= 1
                zetas = [1.0 * big_k / big_l + sigma * (sum([1.0 / lm for lm in lamda[:big_l]]) / big_l - 1.0 / lamda[i]) for i in range(big_l)]
            sj1 = hl.statistic.get_min_entries(big_m, ell, small_m, sigma, lamda, 1, zetas)
            sj2 = hl.statistic.get_min_entries(big_m, ell, small_m, sigma, lamda, 2, zetas)
            result_1.append(sum([lm * sigma / (sigma + lm * sj) for lm, sj in zip(lamda[:big_l], sj1[:big_l])]) + sum(lamda[big_l:]))
            result_2.append(sum([lm * sigma / (sigma + lm * sj) for lm, sj in zip(lamda[:big_l], sj2[:big_l])]) + sum(lamda[big_l:]))
        total_result.append(result_1)
        total_result.append(result_2)

fnc = image_fn.split('.')[0]
with open('modeanalysis_{}'.format('aggregate' if use_aggregate else fnc), 'w') as f:
    pickle.dump({'param':
                    {'big_m': big_m,
                     'small_m': small_m,
                     'big_n': big_n,
                     'sigma': sigma},
                 'label': 'aggregate' if use_aggregate else fnc,
                 'data':
                    [{'x': range(1, big_n+1),
                      'y': result,
                      'mode': mode+1} for mode, result in enumerate(total_result)]}, f)
