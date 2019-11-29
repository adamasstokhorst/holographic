import holographic as hl
import ScriptHelper as Sh

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01
mode = 1

fn = 'img/dragon.png'
use_im_stats = True

if use_im_stats:
    # using image-specific statistics
    lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, fn)
    partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda, mode=mode)
    print partitions
else:
    # using aggregate statistics
    d = Sh.load_data('aggregate_statistics', {'big_m': big_m,
                                              'small_m': small_m,
                                              'big_n': big_n,
                                              'sigma': sigma})
    lamda, psi, partitions = d['lamda'], d['psi'], d['partitions'][mode]

for i in xrange(1, big_n + 1):
    print i,
    image_in = hl.ImageHandler(fn, big_m, mode='r', color_mode='RGB')
    outname = ('SINGLE_{}_{}.png' if use_im_stats else 'SINGLE_{}_aggr_{}.png').format(Sh.get_fname(fn), i)
    image_out = hl.ImageHandler(outname, big_m, mode='w', color_mode='RGB')
    image_out.params(*image_in.params())

    for _, packet in hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=i):
        image_out(packet)

    image_out.close()
