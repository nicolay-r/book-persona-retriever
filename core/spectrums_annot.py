from collections import Counter

import numpy as np

from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def annot_spectrums_in_text(texts_and_speakervars_iter, rev_spectrums):
    """ returns: dictionary of character names,
            where value per every character is a Counter of spectrums
        {
            's_name': Counter([spectrums])
        }
    """

    gd_api = GuttenbergDialogApi()

    d = {}
    for text, speakers in texts_and_speakervars_iter:
        assert(isinstance(text, str))
        assert(isinstance(speakers, list))

        norm_terms = gd_api.normalize_terms(text.split())

        # We limit only for a single speaker.
        speaker = CEBApi.speaker_variant_to_speaker(speakers[0])

        for term in norm_terms:
            if term in rev_spectrums:
                s = rev_spectrums[term]
                bap = "{}-{}".format(s["class"], s["type"])
                if speaker not in d:
                    d[speaker] = Counter()
                d[speaker][bap] += 1

    return d


def __to_vector(d, spectrums_count, v_to_int, ind_func):
    """ NOTE: BAPS numerated from 1
    """
    assert(isinstance(spectrums_count, int))
    assert(callable(v_to_int))
    vector = np.zeros(shape=spectrums_count)
    for spectrum_cat_name, value in d.items():
        ind = ind_func(spectrum_cat_name)
        vector[ind] = v_to_int(value)
    return vector


def annot_to_min_max_grouped(annot, ind_func, do_norm=True, as_vectors=True, spectrums_count=None):

    d = {}

    for s_name, val in annot.items():
        d[s_name] = {}
        dds = d[s_name]
        for k, v in val.items():
            s, t = k.split('-')
            if s not in dds:
                dds[s] = [0, 0]
            dds[s][0 if t == 'low' else 1] = v

    if do_norm:
        for s_name, val in d.items():
            for spectrum, low_high in val.items():
                s = sum(low_high)
                d[s_name][spectrum] = (1.0 * low_high[1] - low_high[0]) / s if s > 0 else 0

    if as_vectors:
        for s_name, val in d.items():
            d[s_name] = __to_vector(val, spectrums_count=spectrums_count,
                                    v_to_int=lambda v: v if do_norm else v[1]-v[0],
                                    ind_func=ind_func)

    return d
