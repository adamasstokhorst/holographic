"""
Provides helper function for the scripts.
"""

import collections
import itertools
import multiprocessing
import numpy
import os
import pickle
import random
import holographic as hl


def ncr(n, r):
    r = min(r, n-r)
    if r < 0:
        return 0
    numer = reduce(lambda a, b: a * b, xrange(n, n-r, -1), 1)
    denom = reduce(lambda a, b: a * b, xrange(1, r+1), 1)
    return numer / denom


def get_fname(path):
    base, _ = os.path.splitext(path)
    return os.path.basename(base)


def save_data(fn, param, new_data):
    try:
        with open(fn, 'r') as f:
            data = pickle.load(f)
    except IOError:
        data = {}

    frozen_param = frozenset(param.items())
    data[frozen_param] = new_data

    with open(fn, 'w') as f:
        pickle.dump(data, f)


def load_data(fn, param):
    with open(fn, 'r') as f:
        data = pickle.load(f)

    return data[frozenset(param.items())]


# to be used with simulated_analysis.py
def worker_task(fn, m, k, l, pd, p, ks, h):
    result = {'key': k,
              'ell': l,
              'out': []}

    for subset in ks:
        packets_mse = []
        if 'overall' in p:
            pd['lost_space'] = subset
        elif 'buildup' in p:
            pd['lost_space'] = subset[l:]
        # TODO: try to make this more efficient? there really is
        #       no need to open the same file multiple times
        for i_data, f_data in hl.helpers.simulate(h(fn, m, 'r')(), **pd):
            packets_mse.append(hl.helpers.mean_squared_error(i_data[0], f_data[0]))
        result['out'].append(numpy.mean(packets_mse))

    return result


def simulation_calc(p, pd, fname, handler, buildup_upper_limit=25, overall_sampling_limit=float('inf'), **kwargs):
    p = dict(p)
    p.update(kwargs)
    if 'buildup' in p:
        print 'Processing {} (build-up)...'.format(fname),
    elif 'overall' in p:
        print 'Processing {} (overall)...'.format(fname),

    im_name = get_fname(fname)
    big_n = p['big_n']
    big_m = p['big_m']
    k_set = None
    x_points = []
    y_points = {k: collections.defaultdict(list) for k in pd}

    total_tasks = 0
    pool = multiprocessing.Pool(processes=3, maxtasksperchild=3)
    queue = multiprocessing.Queue()

    def add_to_queue(out):
        queue.put(out)

    if 'buildup' in p:
        k_set = [random.sample(range(big_n), big_n) for _ in xrange(buildup_upper_limit)]

    for ell in range(1, big_n + 1):
        pd['grid']['ell'] = pd['aggregate']['ell'] = ell
        pd['img']['ell'] = pd['line']['ell'] = ell

        if 'overall' in p:
            if ncr(big_n, ell) <= overall_sampling_limit:
                k_set = list(itertools.combinations(range(big_n), big_n - ell))
            else:
                k_set = []
                while len(k_set) < overall_sampling_limit:
                    sample = random.sample(range(big_n), big_n - ell)
                    if sample not in k_set:
                        k_set.append(sample)

        for key in pd:
            pool.apply_async(worker_task, (fname, big_m, key, ell, pd[key], p, k_set, handler), callback=add_to_queue)
            total_tasks += 1

        x_points.append(ell)

    total_result = collections.defaultdict(list)
    ctr = 1
    print_ctr = 0
    while ctr <= total_tasks:
        val = queue.get()
        total_result[val['key']].append((val['ell'], val['out']))
        if (10 * ctr / total_tasks) > print_ctr:
            print print_ctr,
            print_ctr += 1
        ctr += 1

    for k in pd:
        vals = total_result[k]
        vals.sort()
        for v in zip(*vals)[1]:
            y_points[k]['avg'].append(numpy.mean(v))
            y_points[k]['var'].append(numpy.var(v))

    pool.close()

    data = {'x': x_points, 'label': im_name}
    data.update(y_points)
    save_data('plot_data/' + im_name, p, data)

    print
