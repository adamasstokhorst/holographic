import os
import holographic as hl

big_m = 64
folder = 'img/'

for _, _, fn in os.walk(folder):
    break

fn = [os.path.join(folder, f) for f in fn]

lamda, psi = hl.statistic.calculate_statistic(big_m, hl.ImageHandler, *fn)

print fn
print lamda
print psi
