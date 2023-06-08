from collections import Counter

from utils_gd import GuttenbergDialogApi


def annot_spectrums_in_text(texts_iter, rev_spectrums):

    gd_api = GuttenbergDialogApi()

    d = {}
    for text, speakers in texts_iter:
        norm_terms = gd_api.normalize_terms(text.split())

        # We limit only for a single speaker.
        speaker = speakers[0]

        for term in norm_terms:
            if term in rev_spectrums:
                s = rev_spectrums[term]
                bap = "{}-{}".format(s["class"], s["type"])
                if speaker not in d:
                    d[speaker] = Counter()
                d[speaker][bap] += 1

    return d
