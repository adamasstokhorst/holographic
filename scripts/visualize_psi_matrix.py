"""
Generates a visualization of the orthonormal eigenvalues set; see Figure 3 in
the paper.
"""

import numpy as np
import holographic as hl
import ScriptHelper as Sh


def get_coordinate(x, y):
    layer = max(x, y)
    if layer % 2 != 0:
        return layer**2 + layer + x - y 
    else:
        return layer**2 + layer + y - x


# --- PARAMETERS THAT MAY BE CHANGED ---
big_m = 64
small_m = 8
big_n = 8
sigma = 0.01

# --- END OF PARAMETERS, BEGIN CODE ---
side_length = int((big_m + 1)**0.5)
if side_length**2 != big_m:
    raise ValueError('big_m must be a perfect square. (got {})'.format(big_m))

_, psi_grid = hl.statistic.get_lp_lambda(1, big_m)
_, psi_line = hl.statistic.get_lp_lambda(2, big_m)

params = {'big_m': big_m,
          'small_m': small_m,
          'big_n': big_n,
          'sigma': sigma}
d = Sh.load_data('aggregate_statistics', params)
_, psi_agg = d['lamda'], d['psi']

psi_matrices = {'aggregate': psi_agg,
                'grid': psi_grid,
                'line': psi_line}

patch_order = np.fromfunction(np.vectorize(get_coordinate), (side_length, side_length), dtype=int).flatten()

for k, psi in psi_matrices.items():
    img = hl.handlers.ImageHandler('psi_{}.png'.format(k), big_m, 'w')
    img.params(big_m, big_m, np.zeros((side_length, side_length)))

    for col_index in list(patch_order):
        col = psi[:, col_index]
        img_data = np.array(col)
        img_data.shape = (side_length, side_length)
        img(img_data)

    img.close()

    print 'Saved to psi_{}.png'.format(k)
