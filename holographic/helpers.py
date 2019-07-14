import numpy
import random


def to_operator(projections, n):
    """Converts lists of projections to operators (as matrices)."""
    operator = numpy.zeros((n, len(projections)))
    for i, p in enumerate(projections):
        operator[p-1, i] = 1
    return operator


def white_noise(size, strength):
    """Return Gaussian noise."""
    return numpy.reshape([random.gauss(0, strength) for _ in range(size)], (size, 1))


def band_filter(val, lo, hi):
    """Clips values to be within a certain range."""
    if val < lo:
        return lo
    elif val > hi:
        return hi
    return val


def variance(iterable):
    """Calculates variance of a set."""
    mean = sum(iterable)/len(iterable)
    return 1.0*sum([(mean-x)**2 for x in iterable])/len(iterable)


def euc_norm(iterable):
    """Calculates quadratic mean/Euclidean norm."""
    result = sum([x**2 for x in iterable])
    return (1.0 * result / len(iterable))**.5


def partition(iterable, size, random_mode=False):
    """Partitions an iterable into chunks of equal size with distinct elements (length must be divisible by size).

    Chunks will be distinct as well, sorted in ascending order."""
    import collections
    import itertools

    if isinstance(iterable, collections.Counter) and 0 < len(iterable) < size:
        return

    # convert iterable to a Counter object
    if isinstance(iterable, list):
        condensed_iterable = collections.Counter(iterable)
    elif isinstance(iterable, collections.Counter):
        condensed_iterable = iterable
    else:
        raise ValueError('iterable is neither a list or a Counter object')

    if not random_mode:
        if len(iterable) == 0:
            yield []
        else:
            distinct_members = sorted(list(condensed_iterable))
            # change itertools.combinations to something that emits at random order
            for part in itertools.combinations(distinct_members, size):
                remainder = condensed_iterable - collections.Counter(part)

                # stop if the remaining elements can't make a chunk with distinct elements
                if 0 < len(remainder) < size:
                    continue

                # stop if it's impossible to create further chunks in ascending order
                if len(remainder) > 0 and min(part) > min(remainder):
                    continue

                # recurse by taking a size-chunk and partitioning the remaining
                for remainder_parts in partition(remainder, size):
                    if remainder_parts and list(part) >= remainder_parts[0]:
                        continue
                    # this will be sorted by default
                    yield [list(part)] + remainder_parts
    else:
        while True:
            iter_len = len(list(condensed_iterable.elements()))
            elements = condensed_iterable.most_common()
            result = [list() for _ in range(iter_len//size)]
            flag = [True] * len(result)
            for e, count in elements:
                if count > len([val for val in flag if val]):
                    break
                subset = random.sample([(i, result[i]) for i in range(len(result)) if flag[i]], count)
                for index, member in subset:
                    member.append(e)
                    if len(member) == size:
                        flag[index] = False
            if not any(flag):
                yield sorted(result)
