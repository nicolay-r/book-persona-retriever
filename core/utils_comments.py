from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def iter_text_comments(speakers, book_path_func):
    assert(isinstance(speakers, set))
    assert(callable(book_path_func))

    g_api = GuttenbergDialogApi()
    for k in range(3):

        for book_id, comments in g_api.filter_comment_with_speaker_at_k(book_path_func=book_path_func, k=k):
            for comment in comments:
                # Seek for speaker in a comment.
                for term in comment.split():
                    if GuttenbergDialogApi.is_character(term):
                        if CEBApi.speaker_variant_to_speaker(term) in speakers:
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
