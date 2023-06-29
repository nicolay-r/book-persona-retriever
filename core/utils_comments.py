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
