import numpy
from .helpers import euc_norm, variance, partition


def calculate_statistic(block_size, handler_class, *args, **kwargs):
    """Reads data from given filenames."""
    rxx = numpy.zeros((block_size**2, block_size**2))
    ctr = 0
    for fn in args:
        data = handler_class(fn, block_size, 'r', **kwargs)
        for block in data():
            rxx += numpy.outer(block, block)
            ctr += 1
    rxx /= ctr
    lamda, psi = numpy.linalg.eig(rxx)

    zipped_lamda = sorted(zip(lamda, range(len(lamda))), reverse=True)
    lamda, new_order = zip(*zipped_lamda)
    perm_matrix = numpy.zeros((block_size**2, block_size**2))
    for i, j in enumerate(new_order):
        perm_matrix[j, i] = 1
    psi = numpy.matmul(psi, perm_matrix)

    return lamda, psi


def get_min_entries(big_m, big_n, small_m, vars, l_set):
    # size-check
    l_set = l_set[:big_m]
    if len(l_set) < big_m:
        raise ValueError('lambda set shorter than space size')

    # N * m / M
    addend = 1.0 * big_n * small_m / big_m
    # 1/M \sum_{k=1}^M 1/\lambda_k
    harmonic_lambda = [1.0/x for x in l_set]
    harmonic_average = sum(harmonic_lambda) / big_m

    # calculate zeta_j first to find if any is negative
    zeta_j = [addend - (vars * (1.0/x - harmonic_average)) for x in l_set]

    is_found = True
    try:
        index = [x > 0 for x in zeta_j].index(False)
    except ValueError:
        is_found = False
        index = None

    if is_found:
        # first entry will always be 0, its only for index padding
        sign_array = [0] * big_m

        begin = 1
        end = big_m - 1
        while is_found:
            # index is t in the paper
            index = int((begin + end) / 2)
            sqrt_beta_t = index * vars**.5 / (
                    big_n * small_m + vars * sum(harmonic_lambda[:index]))
            zeta_j = [vars**.5 / sqrt_beta_t - vars / x for x in l_set]
            # zeta_j index starts from 0 instead, this cancels out with the + 1 term
            for i in range(index, big_m):
                zeta_j[i] = 0

            try:
                _ = [x >= 0 for x in zeta_j].index(False)
                sign_array[index] = -1
            except ValueError:
                sign_array[index] = 1

            if sign_array[index] == 1:
                if index == big_m-1 or sign_array[index+1] == -1:
                    is_found = False
                else:
                    begin = index + 1
            else:
                if sign_array[index-1] == 1:
                    # use the value at index - 1 instead, not the current index (since it has negative zeta_j)
                    is_found = False
                    index -= 1
                    sqrt_beta_t = index * vars**.5 / (
                            big_n * small_m + vars * sum(harmonic_lambda[:index]))
                    zeta_j = [vars**.5 / sqrt_beta_t - vars / x for x in l_set]
                    for i in range(index, big_m):
                        zeta_j[i] = 0
                else:
                    end = index - 1

    if index is None:
        index = big_m - 1

    # do initial rounding
    output = map(lambda x: int(round(x)), zeta_j)
    total = sum(output)

    # find distance to closest integer (so this is capped at 0.5, taking the larger integer when at the exact middle)
    distance = zip([int(round(x)) - x for x in zeta_j[:index]], range(big_m))
    distance.sort(key=lambda x: (abs(x[0]), -x[1]))

    if total > big_n * small_m:
        downgrade_list = [x for x in distance if x[0] > 0]
        downgrade_list.sort()
        while total > big_n * small_m:
            _, pos = downgrade_list.pop()
            output[pos] -= 1
            total -= 1

    if len([1 for x in distance if x[0] < 0]) + total < big_n * small_m:
        print zeta_j, big_n
        raise ValueError('arguments incompatible, try something else.')

    if max(output) > big_n:
        while max(output) > big_n:
            diff = [max(x - big_n, 0) for x in output]
            output = map(lambda a, b, c: a - b + c, output, diff, [0] + diff[:-1])

    # start adding to satisfy the requirement that this sum up to at least N*m
    while total < big_n * small_m:
        dist, pos = distance.pop()
        if dist < 0:
            total += 1
            output[pos] += 1

    return output


def zeta(big_n, mul, l_set, var, memo_dict):
    """Calculates zeta_j. Uses memo_dict to speed up calculation."""
    param = (big_n, mul)
    if param not in memo_dict:
        zeta_val = l_set[big_n - 1] / (1 + 1.0 * var / mul / l_set[big_n - 1])
        memo_dict[param] = zeta_val
        return zeta_val
    else:
        return memo_dict[param]


def calculate_partition(space_size, num_subspace, subspace_size, sigma, lamda, erasure_clip=None, partition_limit=30):
    """Randomly finds a partition that allows for a smooth recovery."""
    import collections
    import itertools

    # Given the eigenvalues, find the combination of spaces that yields the best MSE reduction.
    baseline = sum(lamda)
    exact_entries = get_min_entries(space_size, num_subspace, subspace_size, sigma, lamda)

    memo = {}
    picks = reduce(lambda x, y: x + y, [[i+1] * j for i, j in enumerate(exact_entries) if j != 0])
    ctr = collections.Counter()
    ctr.update(picks)
    s_j = collections.Counter()
    s_j.update(exact_entries)

    # Partition the spaces into subspaces.
    partition_list = []
    for parts in partition(picks, subspace_size, random_mode=True):
        partition_list.append(parts)
        if len(partition_list) >= partition_limit:
            break

    # Calculate variance of these partitions to get the smoothest recovery.
    all_variances = []
    for n in range(1, num_subspace+1):
        if n == erasure_clip:
            break
        print num_subspace - n,
        all_variances.append(list())
        for partitions in partition_list:
            values = []
            for subpartition in itertools.combinations(partitions, n):
                subspace_counter = collections.Counter()
                for space in subpartition:
                    subspace_counter.update(space)
                sum_p = sum([zeta(x, y, lamda, sigma, memo) for (x, y) in subspace_counter.most_common()])
                values.append(baseline - sum_p)
            all_variances[-1].append(variance(values))

    output_values = []
    for i, p in enumerate(partition_list):
        p_var = [erasure_stat[i] for erasure_stat in all_variances]
        output_values.append((p, euc_norm(p_var)))
    output_values.sort(key=lambda x: x[1])
    return output_values[0][0]


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
