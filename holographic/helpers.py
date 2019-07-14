import numpy
import random


def to_operator(projections, n):
    operator = numpy.zeros((n, len(projections)))
    for i, p in enumerate(projections):
        operator[p-1, i] = 1
    return operator


def white_noise(size, strength):
    return numpy.reshape([random.gauss(0, strength) for _ in range(size)], (size, 1))


def band_filter(val, lo, hi):
    if val < lo:
        return lo
    elif val > hi:
        return hi
    return val


# def load_image(f, bs, mode='L'):
#     # accepts file-like object, returns image data in numpy matrices -- padded to align with blocks
#     img = Image.open(f).convert(mode)
#     width, height = img.size
#     cols, rows = -(-height / bs * bs), -(-width / bs * bs)
#     band_num = 3 if mode == 'RGB' else 1
#
#     pix_matrix = map(lambda a: numpy.array(list(img.getdata(band=a))) / 256.0, range(band_num))
#     for i in range(band_num):
#         pix_matrix[i].shape = (height, width)
#     img_pixels = map(lambda a: numpy.pad(a, ((0, cols - height), (0, rows - width)), 'constant'), pix_matrix)
#     return width, height, img_pixels
#
#
# def normalize_matrices(ps, bs, space_size):
#     # accepts matrices, returns them centered at 0 and normalized. also returns the original center
#     cols, rows = ps[0].shape
#     averages = []
#     for p in ps:
#         averages.append(numpy.zeros((space_size, 1)))
#         ctr = 0
#         for i, j in itertools.product(range(cols / bs), range(rows / bs)):
#             block = numpy.reshape(p[i * bs:(i + 1) * bs, j * bs:(j + 1) * bs], (space_size, 1))
#             averages[-1] += block
#             ctr += 1
#         averages[-1] /= ctr
#         averages[-1].shape = (bs, bs)
#
#     for i, j in itertools.product(range(cols / bs), range(rows / bs)):
#         for k, p in enumerate(ps):
#             p[i * bs:(i + 1) * bs, j * bs:(j + 1) * bs] -= averages[k]
#
#     for ave in averages:
#         ave.shape = (space_size, 1)
#     return averages, ps
#
#
# def load_statistic(settings):
#     # accepts settings module, returns loaded statistics
#     with open(settings.partition_fn, 'rb') as f:
#         partition = pickle.load(f)
#     with open(settings.psi_fn, 'rb') as f:
#         psi = pickle.load(f)
#     with open(settings.lambda_fn, 'rb') as f:
#         lamda = pickle.load(f)
#     operators = map(lambda a: to_operator(a, settings.big_m), partition)
#     psi_operators = map(lambda a: numpy.dot(a.T, psi.T), operators)
#     r_yy = numpy.diag(lamda)
#     return psi_operators, operators, psi, r_yy
#
#
# def simulate(iterable, settings, ell=1, lost_space=None):
#     """Yield vectors from simulated recovery. Data are assumed to be between -1 and 1, centered at 0."""
#     mod_op, op, psi, r_yy = load_statistic(settings)
#     subspace_size, num_subspace = settings.small_m, settings.big_n
#     sigma = settings.sigma
#
#     if not lost_space:
#         lost_space = random.sample(range(num_subspace), num_subspace - ell)
#     noise = sigma * numpy.eye((num_subspace - len(lost_space)) * subspace_size)
#
#     proj_combi = numpy.concatenate([proj for k, proj in enumerate(op) if k not in lost_space], axis=1)
#     m_matrix = reduce(numpy.dot, [proj_combi.T, r_yy, proj_combi]) + noise
#     m_inv = numpy.linalg.inv(m_matrix)
#     left_mult = reduce(numpy.dot, [psi, r_yy, proj_combi, m_inv])
#
#     for packet in iterable:
#         z_vec = map(lambda a: numpy.dot(a, packet) + white_noise(subspace_size, sigma), mod_op)
#
#         z_combi = reduce(lambda a, b: a + b, [list(z) for l, z in enumerate(z_vec) if l not in lost_space])
#         z_combi = numpy.array(map(lambda a: a[0, 0], z_combi))
#
#         x_hat = numpy.dot(left_mult, z_combi)
#         yield map(lambda x: band_filter(x, -1, 1), x_hat)
