import numpy


def calculate_statistic(block_size, handler_class, *args, **kwargs):
    """Reads data from given filenames."""
    rxx = numpy.zeros((block_size, block_size))
    ctr = 0
    for fn in args:
        data = handler_class(fn, block_size, 'r', **kwargs)
        for blocks in data():
            for block in blocks:
                rxx += numpy.outer([block], [block])
                ctr += 1
    rxx /= ctr
    lamda, psi = numpy.linalg.eig(rxx)

    zipped_lamda = sorted(zip(lamda, range(len(lamda))), reverse=True)
    lamda, new_order = zip(*zipped_lamda)
    perm_matrix = numpy.zeros((block_size, block_size))
    for i, j in enumerate(new_order):
        perm_matrix[j, i] = 1
    psi = numpy.matmul(psi, perm_matrix)

    return lamda, psi


def calculate_zetas(big_m, big_n, small_m, vari, l_set):
    # N * m / M
    addend = 1.0 * big_n * small_m / big_m
    # 1/M \sum_{k=1}^M 1/\lambda_k
    harmonic_lambda = [1.0/x for x in l_set]
    harmonic_average = sum(harmonic_lambda) / big_m

    # calculate zeta_j first to find if any is negative
    zeta_j = [addend - (vari * (1.0 / x - harmonic_average)) for x in l_set]

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
            sqrt_beta_t = index * vari ** .5 / (
                    big_n * small_m + vari * sum(harmonic_lambda[:index]))
            zeta_j = [vari ** .5 / sqrt_beta_t - vari / x for x in l_set]
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
                    sqrt_beta_t = index * vari ** .5 / (
                            big_n * small_m + vari * sum(harmonic_lambda[:index]))
                    zeta_j = [vari ** .5 / sqrt_beta_t - vari / x for x in l_set]
                    for i in range(index, big_m):
                        zeta_j[i] = 0
                else:
                    end = index - 1

    if index is None:
        index = big_m - 1

    return zeta_j, index


def get_min_entries(big_m, big_n, small_m, vari, l_set, mode, zeta_j):
    """Calculate the distribution of subspaces for the greatest MSE reduction."""
    # size-check
    l_set = l_set[:big_m]
    if len(l_set) < big_m:
        raise ValueError('lambda set shorter than space size')

    if mode == 1:
        if zeta_j is None:
            zeta_j, index = calculate_zetas(big_m, big_n, small_m, vari, l_set)
        else:
            index = None

        # do initial rounding
        output = map(lambda x: int(round(x)), zeta_j)
        total = sum(output)

        # find distance to closest integer
        # this is capped at 0.5, taking the larger integer when at the exact middle
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
            print distance
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

        overflow = sum([max(0, a - big_n) for a in output])
        if overflow:
            for i in xrange(len(output)):
                if output[i] >= big_n:
                    output[i] = big_n
                else:
                    if overflow and output[i] < big_n:
                        if overflow >= big_n - output[i]:
                            overflow -= big_n - output[i]
                            output[i] = big_n
                        else:
                            output[i] += overflow
                            overflow = 0
        return output
    elif mode == 2:
        if zeta_j is None:
            zeta_j, _ = calculate_zetas(big_m, big_n, small_m, vari, l_set)

        output = [int(z) for z in zeta_j]
        remainder = big_n * small_m - sum(output)
        index = 0
        while remainder > 0:
            if output[index] < big_n:
                if remainder >= big_n - output[index]:
                    remainder -= big_n - output[index]
                    output[index] = big_n
                else:
                    output[index] += remainder
                    remainder = 0
            index += 1

        overflow = sum([max(0, a - big_n) for a in output])
        if overflow:
            for i in xrange(len(output)):
                if output[i] >= big_n:
                    output[i] = big_n
                else:
                    if overflow and output[i] < big_n:
                        if overflow >= big_n - output[i]:
                            overflow -= big_n - output[i]
                            output[i] = big_n
                        else:
                            output[i] += overflow
                            overflow = 0
        return output
    elif mode == 3:
        return [big_n] * small_m + [0] * (big_m - big_n)
    else:
        raise ValueError('unrecognized mode (got {})'.format(mode))


def zeta(big_n, mul, l_set, var, memo_dict):
    """Calculates zeta_j. Uses memo_dict to speed up calculation."""
    param = (big_n, mul)
    if param not in memo_dict:
        zeta_val = l_set[big_n - 1] / (1 + 1.0 * var / mul / l_set[big_n - 1])
        memo_dict[param] = zeta_val
        return zeta_val
    else:
        return memo_dict[param]


def calculate_partition(space_size, num_subspace, subspace_size, sigma, lamda, mode=1, zeta_j=None):
    """Finds a partition that allows for a smooth recovery."""
    # Given the eigenvalues, find the combination of spaces that yields the best MSE reduction.
    exact_entries = get_min_entries(space_size, num_subspace, subspace_size, sigma, lamda, mode, zeta_j)

    # === OLD ALGORITHM ===
    # Partition the spaces into subspaces.
    """partition = [[0, i, list()] for i in range(num_subspace)]
    for i, sense_count in enumerate(exact_entries):
        ctr = 0
        for k in range(num_subspace):
            if len(partition[k][2]) < subspace_size:
                partition[k][0] += lamda[i]
                partition[k][2].append(i+1)
                ctr += 1
            if ctr == sense_count:
                break
        partition.sort()

    return sorted([x[2] for x in partition])
    """

    # === NEW ALGORITHM ===
    partition = [list() for _ in xrange(num_subspace)]
    subspaces = reduce(lambda a, b: a + b, [[i + 1]*s for i, s in enumerate(exact_entries)])
    for i in xrange(num_subspace * subspace_size):
        partition[i % num_subspace].append(subspaces[i])

    return sorted(partition)


def get_lp_lambda(p_norm, big_m, gamma=0.98, a_constant=0.18):
    """Returns lambda profile using L^p norm."""
    import itertools

    # big_m needs to be a perfect square
    side_length = int((big_m + 1)**0.5)
    if side_length**2 != big_m:
        raise ValueError('big_m must be a perfect square. (got {})'.format(big_m))

    matrix = numpy.zeros((big_m, big_m))
    for i, j in itertools.product(range(1, big_m+1), repeat=2):
        a, b = i / side_length, i % side_length
        p, q = j / side_length, j % side_length
        gamma_power = (numpy.abs(a - p)**p_norm + numpy.abs(b - q)**p_norm)**(1.0 / p_norm)
        matrix[i-1, j-1] = a_constant * gamma**gamma_power

    lamda, psi = numpy.linalg.eig(matrix)
    zipped_lamda = sorted(zip(lamda, range(len(lamda))), reverse=True)
    lamda, new_order = zip(*zipped_lamda)
    perm_matrix = numpy.zeros((big_m, big_m))
    for i, j in enumerate(new_order):
        perm_matrix[j, i] = 1
    psi = numpy.matmul(psi, perm_matrix)

    return lamda, psi
