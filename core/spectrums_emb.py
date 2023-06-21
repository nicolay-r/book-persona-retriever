import numpy as np

from utils_fcp import FcpApi


def filter_by_non_zero(X, y, threshold):
    """ Filters embedding data by non-zero amount threshold
    """
    assert(isinstance(X, list))
    assert(isinstance(threshold, int) or threshold is None)

    if threshold is None:
        return X, y

    xy = zip(X, y)
    xyf = list(filter(lambda pair: np.count_nonzero(pair[0]) > threshold, xy))
    X, y = list(zip(*xyf))
    X = np.array(X)

    return X, y


def convert_to_prompts(X, fcp_api):
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
            prompt.append(lexicon[ind]["low" if spec_val < 0 else "high"])

        prompts.append(" ".join(prompt))

    return prompts
