import holographic as hl
import pickle
import pprint
import collections

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

fn = 'img/dragon.png'
use_im_stats = True

if use_im_stats:
    # using image-specific statistics
    lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=1)
    print partitions
else:
    # using aggregate statistics
    with open('aggregate_statistics', 'r') as f:
        d = pickle.load(f)
        lamda, psi, partitions = d['lamda'], d['psi'], d['partitions']

c = collections.Counter()
c.update([a for p in partitions for a in p])
print(c.most_common())
pprint.pprint(lamda)

for i in range(1, big_n + 1):
    print i,
    image_in = hl.ImageHandler(fn, big_m, mode='r', color_mode='RGB')
    image_out = hl.ImageHandler('true_out_{}_{}'.format(i, fn), big_m, mode='w', color_mode='RGB')
    image_out.params(*image_in.params())

    for _, packet in hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=i):
        image_out(packet)

    image_out.close()
