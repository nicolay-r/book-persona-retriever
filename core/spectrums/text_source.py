from itertools import chain

from core.book.utils import iter_paragraphs_with_n_speakers
from core.dialogue.comments import filter_relevant_text_comments

# TODO. this is expected to be refactored (no need dependence from API).
# TODO. Update 31 May 2024. This code is expected to be located at e_pairs, as it proposes the
# concept aligned in paper: using utterance related comments and non-uterance related.
from api.ceb import CEBApi
from api.gd import GuttenbergDialogApi


def iter_all(speakers, my_api, spectrum_cfg):
    """ This method represent the iterator over the
        whole sources that counted for serving spectrums.
    """

    # Iterate over paragraphs.
    # (Non-utterance related comments)
    paragraphs_it = map(
        lambda t: (t[0].Text, t[1]),
        iter_paragraphs_with_n_speakers(
            speakers=set(speakers),
            n_speakers=spectrum_cfg.speakers_in_paragraph,
            iter_paragraphs=CEBApi.iter_paragraphs(
                iter_book_ids=my_api.book_ids_from_directory(),
                book_by_id_func=my_api.get_book_path),
            paragraph_to_terms=lambda p: CEBApi.separate_character_entries(p.Text).split(),
            cast_to_variant_or_none=lambda term:
                GuttenbergDialogApi.try_parse_character(term, default=None),
            cast_to_id_or_none=lambda variant:
                CEBApi.speaker_variant_to_speaker(variant, return_none=True),
            multi_mentions=False)
    )

    # Iterate over text parts that follows the character utterances.
    # (Utterance related comments)
    g_api = GuttenbergDialogApi()
    comments_it = filter_relevant_text_comments(
        is_term_speaker_func=GuttenbergDialogApi.is_character,
        speaker_positions=spectrum_cfg.comment_speaker_positions,
        speakers=set(speakers),
        cast_to_id_or_none=lambda variant:
            CEBApi.speaker_variant_to_speaker(variant, return_none=True),
        iter_comments_at_k_func=lambda k: g_api.filter_comment_with_speaker_at_k(
            book_path_func=my_api.get_book_path, k=k))

    return chain(paragraphs_it, comments_it)
