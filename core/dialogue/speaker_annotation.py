from collections import OrderedDict

from tqdm import tqdm

# TODO. This should be removed from the core.
from api.ceb import CEBApi
from api.gd import GuttenbergDialogApi

from core.book.book_dialog import BookDialogue


def try_recognize(terms, prefix_lexicon, k_list, is_character_func):
    """ Speaker annotation algorithm.
    """
    assert(callable(is_character_func))

    variant = None
    recognized = False

    # Annotation based on lexicon and prefix.
    for k in k_list:

        if k == 0:
            if len(terms) > 0 and is_character_func(terms[0]):
                # Provide info.
                # NOTE. it is important to convert speaker variation to its book-name format.
                # for appropriate grouping in further.
                variant = terms[0]
                recognized = True

        if prefix_lexicon is not None:
            if len(terms) > k and is_character_func(terms[k]):
                if ' '.join(terms[:k]) in prefix_lexicon:
                    # Provide info.
                    variant = terms[k]
                    recognized = True
                    break

    return recognized, variant


def parse_meta_speaker_id(meta):
    """ Parsing the speaker integer id within the following notation of the dialogue:
            >3#
        where 3 is a result id.
        return: int
    """
    return int(meta[1:-1])


def iter_speaker_annotated_dialogs(dialog_segments_iter_func, recognize_at_positions,
                                   prefix_lexicon=None, **tqdm_kwargs):
    """ This is a speaker annotation algorithm based on guttenberg-dialog
        project with additional annotation from my side (Rusnachenko Nicolay),
        that provides segmenting and author text part (comments) in between
        the segments.
    """
    assert(isinstance(prefix_lexicon, set) or prefix_lexicon is None)

    gd_api = GuttenbergDialogApi()

    pbar = tqdm(desc="Iter dialogue segments", unit="book", **tqdm_kwargs)

    books_seen = set()
    segments = 0
    for book_id, dialog_segments in dialog_segments_iter_func:

        # Update information.
        speakers = set()
        recognized_speakers = {}
        segments += 1
        books_seen.add(book_id)

        # Update progress-bar related info.
        if pbar.n < len(books_seen):
            pbar.update(len(books_seen) - pbar.n)
        pbar.set_postfix({"segments": segments})

        for meta, text in dialog_segments:

            # Considering only comments.
            if meta[0] not in [BookDialogue.META_AUTHOR_COMMENT_LINE,
                               BookDialogue.META_END_OF_DIALOG_LINE]:
                continue

            # Taking meta information and text.
            speaker_id = parse_meta_speaker_id(meta)
            speakers.add(speaker_id)

            # Do analysis.
            terms = gd_api.normalize_terms(text.split())

            recognized, variant = try_recognize(
                terms=terms,
                prefix_lexicon=prefix_lexicon,
                k_list=recognize_at_positions,
                is_character_func=GuttenbergDialogApi.is_character)

            if recognized:
                recognized_speakers[speaker_id] = CEBApi.speaker_variant_to_speaker(variant)

        # Compose to format of actual dialog between speakers
        dialog = OrderedDict()
        for meta, text in dialog_segments:

            if meta[0] not in [BookDialogue.META_DIALOGUE_LINE]:
                continue

            # Initialize the list for the particular speaker.
            speaker_id = parse_meta_speaker_id(meta)
            if speaker_id not in dialog:
                dialog[speaker_id] = []

            dialog[speaker_id].append(text)

        yield dialog, recognized_speakers

    # Manually update progress bar with the amount of the remaining books.
    # Since some of the books might be skipped.
    pbar.update(pbar.total - pbar.n)

