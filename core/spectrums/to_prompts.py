import numpy as np

from core.spectrums.stat import filter_most_distictive, order_traits_by_relevance
from e_pairs.api_fcp import FcpApi


def to_prompts_top_k(X_norm, X_diff, fcp_api, k=None, limit=None):
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
    assert(isinstance(k, int) or k is None)
    assert(isinstance(limit, int) or limit is None)

    if k is not None and limit is not None:
        assert(k < limit)

    # Setup API for using lexicon.
    lexicon = fcp_api.extract_as_lexicon()

    if limit is not None:
        most_distincitve_ids = filter_most_distictive(X_norm, limit)
        print("MOST_DISTINCTIVE:", most_distincitve_ids)
        X_norm = X_norm[:, most_distincitve_ids]
        X_diff = X_diff[:, most_distincitve_ids]
        trait_inds = most_distincitve_ids
    else:
        trait_inds = list(range(X_norm.shape[1]))

    prompts = []
    weights = []
    for i in range(len(X_norm)):

        x_norm = X_norm[i]
        x_diff = X_diff[i]

        # We invalidate traits with the small absolute difference.
        if k is not None:
            bound = list(sorted(x_diff, reverse=True))[k]
            for ii in range(len(x_norm)):
                if abs(x_diff[ii]) < bound:
                    x_norm[ii] = 0

        prompt = []

        x_oridered_inds = order_traits_by_relevance(
            trait_inds=trait_inds, x_norm=x_norm, x_diff=x_diff)

        prompt_weights = []
        weights.append(prompt_weights)

        for ordered_trait_ind, ordered_x_ind in x_oridered_inds[:k]:
            spec_val = x_norm[ordered_x_ind]

            if spec_val == 0:
                continue

            spectrum_ind = fcp_api.ind_to_spectrum(ordered_trait_ind)
            prompt.append(lexicon[spectrum_ind][fcp_api.float_to_spectrum_key(spec_val)])
            prompt_weights.append(spec_val)

        prompts.append(" ".join(prompt))

    return prompts, weights
