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


def mask_text_entities(text, mask_template="_"):
    g_api = GuttenbergDialogApi()

    terms = text.split(' ')

    inds_to_mask = []
    for term_ind, term in enumerate(terms):
        if g_api.has_character(term):
            inds_to_mask.append(term_ind)

    for i in inds_to_mask:
        terms[i] = mask_template

    return " ".join(terms)
