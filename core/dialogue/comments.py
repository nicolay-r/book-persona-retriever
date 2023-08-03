from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def filter_relevant_text_comments(speaker_positions, iter_comments_at_k_func, speakers):
    assert(isinstance(speaker_positions, list))
    assert(callable(iter_comments_at_k_func))
    assert(isinstance(speakers, set))

    for k in speaker_positions:
        for book_id, comments in iter_comments_at_k_func(k):
            for comment in comments:

                # Seek for speaker in a comment.
                for term in comment.split():

                    if not GuttenbergDialogApi.is_character(term):
                        continue
                    if CEBApi.speaker_variant_to_speaker(term) not in speakers:
                        continue

                    yield comment, [term]
                    break


def iter_terms_with_speakers(terms, map_func=None):
    assert(callable(map_func) or map_func is None)

    g_api = GuttenbergDialogApi()

    inds_to_mask = []
    for term_ind, term in enumerate(terms):
        if g_api.has_character(term):
            inds_to_mask.append(term_ind)

    if map_func is not None:
        for ind in inds_to_mask:
            terms[ind] = map_func(terms[ind])

    return terms


def mask_text_entities(text, mask_template="_"):
    terms = iter_terms_with_speakers(
        terms=text.split(' '), map_func=lambda _: mask_template)
    return " ".join(terms)
