import numpy as np

from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI


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

    # Z  utilized as extra axis.
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


FILTER_PRESETS = {
    "original-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=50, paint_func=None, gt=True),
    "all-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=None, paint_func=None, gt=True),
    "z-geq10-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=9, paint_func=None, gt=True),
    "z-geq5-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=4, paint_func=None, gt=True),
    "z-ge50-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=50, paint_func=None, gt=True),
    "z-le2-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=2, paint_func=None, gt=False),
    "z-le2-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=2, paint_func=lambda nzc: str(nzc) if nzc <= 2 else "others", gt=False)
}


def _convert_to_prompts(X, fcp_api):
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
            prompt.append(lexicon[ind]["low" if spec_val < 0 else "high"])

        prompts.append(" ".join(prompt))

    return prompts


def _convert_to_prompts_limited_ordered(X, fcp_api, limit):
    """ This algo counts only the distinctive WITHOUT THEIR FREQUENCIES.
    """
    assert(isinstance(X, list))
    assert(isinstance(fcp_api, FcpApi))
    assert(isinstance(limit, int))

    # Setup API for using lexicon.
    lexicon = fcp_api.extract_as_lexicon()

    prompts = []
    for x in X:
        prompt = []

        ix = list(sorted(enumerate(np.absolute(x)), key=lambda item: item[1], reverse=True))[:limit]
        inds, _ = list(zip(*ix))

        for ind in inds[:limit]:

            spec_val = x[ind]

            if spec_val == 0:
                continue

            ind = fcp_api.ind_to_spectrum(ind)
            prompt.append(lexicon[ind]["low" if spec_val < 0 else "high"])

        prompts.append(" ".join(prompt))

    return prompts


##########################################
# This is a dictionary of preset functions
##########################################
PROMPT_PRESETS = {
    # This is a first revision when we keep everything.
    "prompt_original": lambda X, fcp_api: _convert_to_prompts(X=X, fcp_api=fcp_api),
    "prompt_most_imported_limited_10": lambda X, fcp_api: _convert_to_prompts_limited_ordered(X=X, fcp_api=fcp_api, limit=10),
    "prompt_most_imported_limited_8": lambda X, fcp_api: _convert_to_prompts_limited_ordered(X=X, fcp_api=fcp_api, limit=8),
    "prompt_most_imported_limited_5": lambda X, fcp_api: _convert_to_prompts_limited_ordered(X=X, fcp_api=fcp_api, limit=5)
}
