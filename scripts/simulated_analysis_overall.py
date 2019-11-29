import itertools
import random
import numpy
import holographic as hl
import ScriptHelper as Sh

# list of filepaths
fnames = ['img/bratan.jpg', 'img/dragon.png', 'img/fly.jpeg', 'img/bees.jpg', 'img/dish.jpg', 'img/owl.jpg']
# parameters
big_m = 64
small_m = 8
big_n = 8
sigma = 0.01
mode = 1
# number of combinations to sample
upper_limit = float('inf')

handler = hl.ImageHandler

params = {'big_m': big_m, 'small_m': small_m, 'big_n': big_n, 'sigma': sigma}
d = Sh.load_data('aggregate_statistics', params)
d['partitions'] = d['partitions'][mode]
d.update(params)

params['mode'] = mode
params['overall'] = True

for fname in fnames:
    print 'Processing {}...'.format(fname),

    # make a copy for image-specific statistics
    s = dict(d)
    s['lamda'], s['psi'] = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fname)
    s['partitions'] = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, s['lamda'], mode=mode)

    x_points = []
    y_points = []
    y_points_s = []
    for ell in range(1, big_n + 1):
        print ell,
        s['ell'] = d['ell'] = ell

        if Sh.ncr(d['big_n'], ell) <= upper_limit:
            k_set = list(itertools.combinations(range(big_n), big_n - ell))
        else:
            k_set = []
            while len(k_set) < upper_limit:
                sample = random.sample(range(big_n), big_n - ell)
                if sample not in k_set:
                    k_set.append(sample)

        total_mse = total_mse_s = 0.0
        ctr = 0
        s['lost_space'] = d['lost_space'] = None
        for subset in k_set:
            s['lost_space'] = d['lost_space'] = subset
            for i_data, f_data in hl.helpers.simulate(handler(fname, big_m, 'r')(), **s):
                in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
                total_mse_s += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
            for i_data, f_data in hl.helpers.simulate(handler(fname, big_m, 'r')(), **d):
                in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
                total_mse += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
                ctr += 1

        total_mse /= ctr
        total_mse_s /= ctr
        x_points.append(ell)
        y_points.append(total_mse)
        y_points_s.append(total_mse_s)

    im_name = Sh.get_fname(fname)
    Sh.save_data('plot_data/' + im_name, params, {'x': x_points,
                                                  'y': y_points,
                                                  'y2': y_points_s,
                                                  'label': im_name})

    print
