from functools import cmp_to_key

import numpy as np


def filter_most_distictive(X_norm, limit):
    """ X_norm: matrix of shape [speaker, traits]
        limit: int
    """
    assert(isinstance(limit, int))
    traits = np.mean(np.absolute(X_norm), axis=0)
    trait_ids = list(range(len(traits)))
    most_distinctive = sorted(trait_ids, key=lambda trait_id: traits[trait_id], reverse=True)[:limit]
    return most_distinctive


def order_traits_by_relevance(trait_inds, x_norm, x_diff):

    def __compare(a_norm, a_diff, b_norm, b_diff):

        if a_norm < b_norm:
            return -1
        elif a_norm > b_norm:
            return 1
        else:
            if a_diff < b_diff:
                return -1
            elif a_diff > b_diff:
                return 1
            return 0

    x_inds = list(range(len(x_norm)))
    traits_and_x_sorted = list(sorted(
        list(zip(trait_inds, x_inds, np.absolute(x_norm))),
        key=cmp_to_key(lambda a, b: __compare(a[2], abs(x_diff[a[1]]), b[2], abs(x_diff[b[1]]))),
        reverse=True))

    ordered_trait_inds, ordered_x_inds, _ = list(zip(*traits_and_x_sorted))

    return list(zip(ordered_trait_inds, ordered_x_inds))


def filter_by_non_zero(X, y, z=None, threshold=None, paint_func=None, gt=True):
    """ Filters embedding data by non-zero amount threshold
    """
    assert(isinstance(X, list))
    assert(isinstance(threshold, int) or threshold is None)
    assert(len(X) == len(y))
    assert(callable(paint_func) or paint_func is None)

    def __fmt_output(X_arg, y_arg):
        return np.array(X_arg), y_arg

    def __cmp(a, b):
        return a > b if gt else a < b

    if threshold is None:
        return __fmt_output(X, y)

    # Z utilized as extra axis.
    z = X if z is None else z

    xyz = zip(X, y, z)
    xyzf = list(filter(lambda pair: __cmp(a=np.count_nonzero(pair[2]), b=threshold), xyz))

    if len(xyzf) == 0:
        raise Exception("No elements after filtering. Check threshold criteria (threshold={})".format(threshold))

    X, y, _ = list(zip(*xyzf))

    if paint_func is not None:
        y = []
        for x in X:
            y.append((paint_func(np.count_nonzero(x))))

    return __fmt_output(X, y)
