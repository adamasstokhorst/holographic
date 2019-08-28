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
fnames = ['img/saltharvest.jpg', 'img/greenfrog.jpg', 'img/raflesia.jpg', 'img/plane.jpg', 'img/snowbird.jpg']
# number of combinations to sample
upper_limit = 50
handler = hl.ImageHandler

with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)

for fname in fnames:
    print 'Processing {}...'.format(fname),
    x_points = []
    y_points = []
    for ell in range(1, d['big_n'] + 1):
        print ell,
        d['ell'] = ell

        # if ncr(d['big_n'], ell) <= upper_limit:
        #     k_set = list(itertools.combinations(range(d['big_n']), d['big_n'] - ell))
        # else:
        #     k_set = []
        #     while len(k_set) < upper_limit:
        #         sample = random.sample(range(d['big_n']), d['big_n'] - ell)
        #         if sample not in k_set:
        #             k_set.append(sample)

        total_mse = 0.0
        ctr = 0
        # d['lost_space'] = None
        for _ in range(upper_limit):
            # d['lost_space'] = subset
            for i_data, f_data in hl.helpers.simulate(handler(fname, d['big_m'], 'r')(), **d):
                in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
                total_mse += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
                ctr += 1

        total_mse /= ctr
        x_points.append(ell)
        y_points.append(total_mse)

    with open('plot_data/' + fname.split('/')[-1], 'wb') as f:
        pickle.dump({'x': x_points,
                     'y': y_points,
                     'label': fname.split('/')[-1]}, f)

    print
