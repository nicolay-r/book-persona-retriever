import numpy as np
from functools import cmp_to_key
from utils_fcp import FcpApi


def to_prompts(X, fcp_api):
    """ This is an original versions of the prompting when all non-zero features were considered.
    """
    assert(isinstance(X, list))
    assert(isinstance(fcp_api, FcpApi))

    # Setup API for using lexicon.
    lexicon = fcp_api.extract_as_lexicon()

    prompts = []
    for x in X:
        prompt = []
        for i, spec_val in enumerate(x):

            if spec_val == 0:
                continue

            ind = fcp_api.ind_to_spectrum(i)
            prompt.append(lexicon[ind][fcp_api.float_to_spectrum_key(spec_val)])

        prompts.append(" ".join(prompt))

    return prompts


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
            return

    traits_and_x_sorted = list(sorted(
        zip(trait_inds, np.absolute(x_norm)),
        key=cmp_to_key(lambda a, b: __compare(a[1], abs(x_diff[a[0]]), b[1], abs(x_diff[b[0]]))),
        reverse=True))

    x_inds, _ = list(zip(*traits_and_x_sorted))

    return x_inds


def to_prompts_top_k(X_norm, X_diff, fcp_api, k, limit=None):
    """ k: int
            amount of the traits to be chosen per every speaker for
            prompt composition.
        limit: None or int
            this is comes from the ALOHA paper where authors experiment
            with the particular amount of the most-frequent traits
            among which the final selection of the traits is performed:
            https://github.com/nicolay-r/chatbot_experiments/issues/27
    """
    assert(isinstance(X_norm, np.ndarray))
    assert(isinstance(X_diff, np.ndarray))
    assert(len(X_norm) == len(X_diff))
    assert(isinstance(fcp_api, FcpApi))
    assert(isinstance(k, int))
    assert(isinstance(limit, int) or limit is None)

    # Setup API for using lexicon.
    lexicon = fcp_api.extract_as_lexicon()

    if limit is not None:
        most_distincitve_ids = filter_most_distictive(X_norm, k)
        X_norm = X_norm[:, most_distincitve_ids]
        X_diff = X_diff[:, most_distincitve_ids]
        trait_inds = most_distincitve_ids
    else:
        trait_inds = list(range(X_norm.shape[1]))

    prompts = []
    for i in range(len(X_norm)):

        x_norm = X_norm[i]
        x_diff = X_diff[i]

        # We invalidate traits with the small absolute difference.
        bound = list(sorted(x_diff, reverse=True))[k]
        for ii in range(len(x_norm)):
            if abs(x_diff[ii]) < bound:
                x_norm[ii] = 0

        prompt = []

        x_oridered_inds = order_traits_by_relevance(
            trait_inds=trait_inds, x_norm=x_norm, x_diff=x_diff)

        for ind in x_oridered_inds[:k]:
            spec_val = x_norm[ind]

            if spec_val == 0:
                continue

            ind = fcp_api.ind_to_spectrum(ind)
            prompt.append(lexicon[ind][fcp_api.float_to_spectrum_key(spec_val)])

        prompts.append(" ".join(prompt))

    return prompts


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
