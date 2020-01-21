import itertools
import collections
import random
import numpy
import holographic as hl
import ScriptHelper as Sh
import multiprocessing


def worker_task(fn, bm, key, l, data_dict, params, ks, handler):
    result = {'key': key,
              'ell': l,
              'out': []}
    
    for subset in ks:
        if 'overall' in params:
            data_dict['lost_space'] = subset
        elif 'buildup' in params:
            data_dict['lost_space'] = subset[l:]
        for i_data, f_data in hl.helpers.simulate(handler(fn, bm, 'r')(), **data_dict):
            result['out'].append(numpy.sum([(x - y)**2 for x, y in zip(i_data[0], f_data[0])]))
    
    return result


def simulation_calc(p, pd, **kwargs):
    p = dict(p)
    p.update(kwargs)
    if 'buildup' in p:
        print 'Processing {} (build-up)...'.format(fname),
    elif 'overall' in p:
        print 'Processing {} (overall)...'.format(fname),

    big_n = p['big_n']
    x_points = []
    y_points = {k: collections.defaultdict(list) for k in pd}
    
    if 'buildup' in p:
        k_set = [random.sample(range(big_n), big_n) for _ in xrange(buildup_upper_limit)]

    pool = multiprocessing.Pool()
    futures = []
    
    for ell in range(1, big_n + 1):
        print ell,
        pd['grid']['ell'] = pd['aggregate']['ell'] = ell
        pd['img']['ell'] = pd['line']['ell'] = ell

        if 'overall' in p:
            if Sh.ncr(big_n, ell) <= overall_sampling_limit:
                k_set = list(itertools.combinations(range(big_n), big_n - ell))
            else:
                k_set = []
                while len(k_set) < overall_sampling_limit:
                    sample = random.sample(range(big_n), big_n - ell)
                    if sample not in k_set:
                        k_set.append(sample)
        
        for k in pd:
            futures.append(pool.apply_async(worker_task, (fname, big_m, k, ell, pd[k], p, k_set, handler)))

        x_points.append(ell)
    
    total_result = collections.defaultdict(list)
    for future in futures:
        val = future.get()
        total_result[val['key']].append((val['ell'], val['out']))
    
    for k, ord_list in total_result.items():
        ord_list.sort()
        vals = zip(*ord_list)[1]
        for v in vals:
            y_points[k]['avg'].append(numpy.mean(v))
            y_points[k]['var'].append(numpy.var(v))

    data = {'x': x_points, 'label': im_name}
    data.update(y_points)
    Sh.save_data('plot_data/' + im_name, p, data)

    print


if __name__ == '__main__':
    # list of filepaths
    fnames = ['img/fly.jpeg']
    # parameters
    big_m = 64
    small_m = 8
    big_n = 8
    sigma = 0.01
    mode = 1
    # number of combinations to sample
    buildup_upper_limit = 25
    overall_sampling_limit = float('inf')

    handler = hl.ImageHandler

    print 'Calculating simulated recovery results...'
    print '  Parameters: M={}, m={}, N={}, sigma^2={} on mode {}'.format(big_m, small_m, big_n, sigma, mode)

    params = {'big_m': big_m, 'small_m': small_m, 'big_n': big_n, 'sigma': sigma}

    # Prepare all the parameters
    param_dict = {'aggregate': Sh.load_data('aggregate_statistics', params)}
    param_dict['aggregate']['partitions'] = param_dict['aggregate']['partitions'][mode]
    param_dict['aggregate'].update(params)

    param_dict['grid'] = dict(param_dict['aggregate'])
    param_dict['grid']['lamda'], param_dict['grid']['psi'] = hl.statistic.get_lp_lambda(1, big_m)
    param_dict['grid']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                        param_dict['grid']['lamda'], mode=mode)

    param_dict['line'] = dict(param_dict['aggregate'])
    param_dict['line']['lamda'], param_dict['line']['psi'] = hl.statistic.get_lp_lambda(2, big_m)
    param_dict['line']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                        param_dict['line']['lamda'], mode=mode)

    params['mode'] = mode

    for fname in fnames:
        # make a copy for image-specific statistics
        param_dict['img'] = dict(param_dict['aggregate'])
        param_dict['img']['lamda'], param_dict['img']['psi'] = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fname)
        param_dict['img']['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma,
                                                                           param_dict['img']['lamda'], mode=mode)
        im_name = Sh.get_fname(fname)
        
        simulation_calc(params, param_dict, buildup=True)
        simulation_calc(params, param_dict, overall=True)
