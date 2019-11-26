import itertools
import pickle
import random
import numpy
import holographic as hl


def ncr(n, r):
    r = min(r, n-r)
    if r < 0:
        return 0
    numer = reduce(lambda a, b: a * b, xrange(n, n-r, -1), 1)
    denom = reduce(lambda a, b: a * b, xrange(1, r+1), 1)
    return numer / denom


# list of filepaths
fnames = ['img/bratan.jpg', 'img/beak.jpg', 'img/fly.jpeg', 'img/bees.jpg', 'img/dish.jpg', 'img/bear.jpg']
# number of combinations to sample
upper_limit = float('inf')
handler = hl.ImageHandler

with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)

for fname in fnames:
    print 'Processing {}...'.format(fname),

    # make a copy for image-specific statistics
    s = dict(d)
    s['lamda'], s['psi'] = hl.statistic.calculate_statistic(d['big_m'], hl.ImageHandler, fname)
    s['partitions'] = hl.statistic.calculate_partition(d['big_m'], d['big_n'], d['small_m'], d['sigma'], s['lamda'])

    x_points = []
    y_points = []
    y_points_s = []
    for ell in range(1, d['big_n'] + 1):
        print ell,
        s['ell'] = d['ell'] = ell

        if ncr(d['big_n'], ell) <= upper_limit:
            k_set = list(itertools.combinations(range(d['big_n']), d['big_n'] - ell))
        else:
            k_set = []
            while len(k_set) < upper_limit:
                sample = random.sample(range(d['big_n']), d['big_n'] - ell)
                if sample not in k_set:
                    k_set.append(sample)

        total_mse = total_mse_s = 0.0
        ctr = 0
        s['lost_space'] = d['lost_space'] = None
        for subset in k_set:
            s['lost_space'] = d['lost_space'] = subset
            for i_data, f_data in hl.helpers.simulate(handler(fname, s['big_m'], 'r')(), **s):
                in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
                total_mse_s += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
            for i_data, f_data in hl.helpers.simulate(handler(fname, d['big_m'], 'r')(), **d):
                in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
                total_mse += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
                ctr += 1

        total_mse /= ctr
        total_mse_s /= ctr
        x_points.append(ell)
        y_points.append(total_mse)
        y_points_s.append(total_mse_s)

    with open('plot_data/' + fname.split('/')[-1], 'w') as f:
        pickle.dump({'x': x_points,
                     'y': y_points,
                     'y2': y_points_s,
                     'label': fname.split('/')[-1]}, f)

    print
