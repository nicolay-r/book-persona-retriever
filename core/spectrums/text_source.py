from itertools import chain

from core.book.utils import iter_paragraphs_with_n_speakers
from core.dialogue.comments import filter_relevant_text_comments
# TODO. this is expected to be refactored (no need dependence from API).
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_all(speakers, my_api):
    """ This method represent the iterator over the
        whole sources that counted for serving spectrums.
    """

    # Iterate over paragraphs.
    paragraphs_it = map(
        lambda t: (t[0].Text, t[1]),
        iter_paragraphs_with_n_speakers(
            speakers=set(speakers),
            n_speakers=my_api.spectrum_speakers_in_paragraph,
            iter_paragraphs=CEBApi.iter_paragraphs(
                iter_book_ids=my_api.book_ids_from_directory(),
                book_by_id_func=my_api.get_book_path)))

    # Iterate over comments.
    g_api = GuttenbergDialogApi()
    comments_it = filter_relevant_text_comments(
        is_term_speaker_func=GuttenbergDialogApi.is_character,
        speaker_positions=MyAPI.spectrum_comment_speaker_positions,
        speakers=set(speakers),
        iter_comments_at_k_func=lambda k: g_api.filter_comment_with_speaker_at_k(
            book_path_func=my_api.get_book_path, k=k))

    return chain(paragraphs_it, comments_it)
