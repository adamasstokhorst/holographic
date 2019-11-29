import itertools
import collections
import holographic as hl
import ScriptHelper as Sh

# list of filepaths
fnames = ['img/bratan.jpg', 'img/dragon.png', 'img/fly.jpeg', 'img/bees.jpg', 'img/dish.jpg', 'img/owl.jpg']
# parameters
big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

params = {'big_m': big_m,
          'small_m': small_m,
          'big_n': big_n,
          'sigma': sigma}

fnames += ['*AGGREGATE*']

print 'Calculating theoretical best results...'
print '  Parameters: M={}, m={}, N={}, sigma^2={}'.format(big_m, small_m, big_n, sigma)

for image_fn in fnames:
    if image_fn == '*AGGREGATE*':
        print 'Processing aggregate results...'
        d = Sh.load_data('aggregate_statistics', params)
        lamda, partitions = d['lamda'], d['partitions']
    else:
        print 'Processing {}...'.format(image_fn)
        lamda, _ = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, image_fn)
        partitions = {mode: hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode) for mode in range(1, 3+1)}

    total_result = []

    # calculate best possible MSE reduction using each partition strategy
    for mode in range(1, 4+1):
        if mode <= 3:
            partition = partitions[mode]
            baseline = sum(lamda)
            memo = {}
            result = []

            for ell in range(1, big_n+1):
                best_sum = 0
                for subset in itertools.combinations(range(big_n), ell):
                    subspace_counter = collections.Counter()
                    for i in subset:
                        subspace_counter.update(partition[i])
                    sum_p = sum([hl.statistic.zeta(x, y, lamda, sigma, memo) for (x, y) in subspace_counter.most_common()])
                    best_sum = sum_p if sum_p > best_sum else best_sum
                result.append(baseline - best_sum)

            total_result.append(result)
        else:
            # mode "4" is for theoretical best
            result = []
            for ell in range(1, big_n+1):
                big_k = ell * small_m
                big_l = big_m
                zetas = [1.0 * big_k / big_l + sigma * (sum([1.0 / lm for lm in lamda[:big_l]]) / big_l - 1.0 / lamda[i]) for i in range(big_l)]
                while any([z<0 for z in zetas]):
                    big_l -= 1
                    zetas = [1.0 * big_k / big_l + sigma * (sum([1.0 / lm for lm in lamda[:big_l]]) / big_l - 1.0 / lamda[i]) for i in range(big_l)]
                result.append(sum([lm * sigma / (sigma + lm * z) for lm, z in zip(lamda[:big_l], zetas[:big_l])]) + sum(lamda[big_l:]))
            total_result.append(result)

    data_fn = 'aggregate' if image_fn == '*AGGREGATE*' else Sh.get_fname(image_fn)
    data = {'label': 'aggregate' if image_fn == '*AGGREGATE*' else data_fn,
            'data': [{'x': range(1, big_n+1),
                      'y': result,
                      'mode': mode+1} for mode, result in enumerate(total_result)]}

    Sh.save_data('modeanalysis_{}'.format(data_fn), params, data)
