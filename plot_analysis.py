import itertools
import pickle
import random
from matplotlib import pyplot
import numpy
import holographic as hl


def ncr(n, r):
    r = min(r, n-r)
    if r < 0:
        return 0
    numer = reduce(lambda a, b: a * b, xrange(n, n-r, -1), 1)
    denom = reduce(lambda a, b: a * b, xrange(1, r+1), 1)
    return numer / denom


fname = 'img/lena.jpg'
handler = hl.ImageHandler
upper_limit = 50

with open('aggregate_statistics', 'r') as f:
    d = pickle.load(f)

x_points = []
y_points = []
for ell in range(1, d['big_n'] + 1):
    d['ell'] = ell

    if ncr(d['big_n'], ell) <= upper_limit:
        k_set = list(itertools.combinations(range(d['big_n']), d['big_n'] - ell))
    else:
        k_set = []
        while len(k_set) < upper_limit:
            sample = random.sample(range(d['big_n']), d['big_n'] - ell)
            if sample not in k_set:
                k_set.append(sample)

    total_mse = 0.0
    ctr = 0
    d['lost_space'] = None
    for subset in k_set:
        d['lost_space'] = subset
        for i_data, f_data in hl.helpers.simulate(handler(fname, d['big_m'], 'r')(), **d):
            in_vec, out_vec = numpy.array(i_data), numpy.array(f_data)
            total_mse += sum(((in_vec - out_vec)**2).flatten()) / in_vec.size
            ctr += 1

    total_mse /= ctr
    x_points.append(ell)
    y_points.append(total_mse)

fig, axes = pyplot.subplots(1)
fig.set_size_inches(12, 9)
axes.grid(True, linestyle='dotted')
axes.set_ylabel('(Log) Mean squared error', fontsize=24)
axes.set_xlabel(r'$\ell$', fontsize=24)
axes.semilogy(x_points, y_points, '.b-')
pyplot.show()
