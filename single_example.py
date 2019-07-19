import holographic as hl

big_m = 64
small_m = 8
big_n = 8
sigma = 0.05

lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, 'img/lena.jpg')
partitions = hl.statistic.calculate_partition(big_m, big_n, small_m, sigma, lamda)

image_in = hl.ImageHandler('img/lena.jpg', big_m, mode='r')
image_out = hl.ImageHandler('lena_out.jpg', big_m, mode='w')
image_out.params(*image_in.params())

for packet in hl.helpers.simulate(image_in(), psi, lamda, partitions, big_m, small_m, big_n, sigma, ell=4):
    image_out(packet)

image_out.close()
