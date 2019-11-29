import pickle
import os.path


def ncr(n, r):
    r = min(r, n-r)
    if r < 0:
        return 0
    numer = reduce(lambda a, b: a * b, xrange(n, n-r, -1), 1)
    denom = reduce(lambda a, b: a * b, xrange(1, r+1), 1)
    return numer / denom


def get_fname(path):
    base, _ = os.path.splitext(path)
    return os.path.basename(base)


def save_data(fn, param, new_data):
    try:
        with open(fn, 'r') as f:
            data = pickle.load(f)
    except IOError:
        data = {}

    frozen_param = frozenset(param.items())
    data[frozen_param] = new_data

    with open(fn, 'w') as f:
        pickle.dump(data, f)


def load_data(fn, param):
    with open(fn, 'r') as f:
        data = pickle.load(f)

    return data[frozenset(param.items())]
