import pprint
import collections
import random
import holographic as hl
import ScriptHelper as Sh

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01
mode = 1

fn = 'img/oldlady.jpg'

# the following accepts:
#   'image' - image specific statistics
#   'aggr'  - aggregate statistics
#   'grid'  - grid-metric (L^1) statistics
#   'line'  - line-metric (L^2) statistics
stats_to_use = 'image'

# if False, use random selection of subspaces instead
do_buildup = True

simul_mode = 'build-up' if do_buildup else 'random'
fn_prefix = 'BUILDUP' if do_buildup else 'SINGLE'
print 'Simulating {} recovery on {}'.format(simul_mode, fn)
print '  Parameters: M={}, m={}, N={}, sigma^2={} on mode {}'.format(big_m, small_m, big_n, sigma, mode)
print '  Using {} statistics...'.format('aggregate' if stats_to_use == 'aggr' else stats_to_use)

if stats_to_use == 'image':
    # using image-specific statistics
    lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
elif stats_to_use == 'aggr':
    # using aggregate statistics
    d = Sh.load_data('aggregate_statistics', {'big_m': big_m,
                                              'small_m': small_m,
                                              'big_n': big_n,
                                              'sigma': sigma})
    lamda, psi, partitions = d['lamda'], d['psi'], d['partitions'][mode]
elif stats_to_use == 'grid':
    lamda, psi = hl.statistic.get_lp_lambda(1, big_m)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
elif stats_to_use == 'line':
    lamda, psi = hl.statistic.get_lp_lambda(2, big_m)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
else:
    raise ValueError('unrecognized statistic parameter. (got {})'.format(stats_to_use))

counter = collections.Counter(reduce(lambda a, b: a + b, partitions))
print 'Partitions: ',
pprint.pprint(partitions)
print 'Sampling distribution: '
print ' ', ' '.join(['[{}]{}'.format(*x) for x in counter.most_common()])
print 'Lambdas: ',
pprint.pprint(lamda)

if do_buildup:
    sp = random.sample(range(big_n), big_n)

print 'Processing ell =',
for i in xrange(1, big_n + 1):
    print i,
    image_in = hl.ImageHandler(fn, big_m, mode='r', color_mode='RGB')
    fstring = '{}_{}_{}.png' if stats_to_use == 'image' else '{{}}_{{}}_{}_{{}}.png'.format(stats_to_use)
    outname = fstring.format(fn_prefix, Sh.get_fname(fn), i)
    image_out = hl.ImageHandler(outname, big_m, mode='w', color_mode='RGB')
    image_out.params(*image_in.params())

    if do_buildup:
        g = hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, lost_space=sp[i:])
    else:
        g = hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=i)

    for _, packet in g:
        image_out(packet)

    image_out.close()

print
