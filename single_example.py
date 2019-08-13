import holographic as hl

big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

fn = 'painter.jpeg'

lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, 'img/' + fn)
partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda)

image_in = hl.ImageHandler('img/' + fn, big_m, mode='r', color_mode='RGB')
image_out = hl.ImageHandler('out_' + fn, big_m, mode='w', color_mode='RGB')
image_out.params(*image_in.params())

for _, packet in hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=2):
    image_out(packet)

image_out.close()
