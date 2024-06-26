from collections import Counter

from tqdm import tqdm

from core.book.paragraph import Paragraph


def iter_paragraphs_with_n_speakers(speakers, iter_paragraphs, paragraph_to_terms,
                                    cast_to_id_or_none, cast_to_variant_or_none,
                                    n_speakers=1, multi_mentions=False):
    """ Iterate text paragraphs which contains only N mentioned speakers from `speakers` set.
        based on the Character-based-embedding API.

        multi_mentions: bool
            denotes whether the same speaker could be mentioned multiple times, i.e. counted as mentioned once.

        NOTE:
        * This method excluded cases with such speakers that mentioned in paragraph but not mentioned in `speakers`
        * It is important that each speaker represent in a form of separated word /
            or speaker recognition function support this case. (#43)
    """
    assert (isinstance(speakers, set))
    assert (callable(paragraph_to_terms))
    assert (callable(cast_to_id_or_none))
    assert (isinstance(n_speakers, int) and n_speakers >= 0)
    assert (isinstance(multi_mentions, bool))

    s_count = Counter()
    pbar = tqdm(iter_paragraphs, "Iter Paragraphs")
    for p in pbar:
        assert(isinstance(p, Paragraph))

        pbar.set_postfix({
            'kept': s_count["kept"],
            'total': s_count['total']
        })

        s_count["total"] += 1

        p_speakers = []
        has_others = False
        for term in paragraph_to_terms(p):

            # {book_charindex_variant}
            speaker_variant = cast_to_variant_or_none(term)
            if speaker_variant is None:
                continue

            # {book_charindex}
            speaker_id = cast_to_id_or_none(speaker_variant)
            if speaker_id is None:
                continue

            if speaker_id in speakers:
                p_speakers.append(speaker_variant)
            else:
                has_others = True

        # Cast to set and back in the case if `use_set` flag is raised.
        p_speakers = list(set(p_speakers)) if multi_mentions else p_speakers

        if len(p_speakers) != n_speakers or has_others:
            continue

        # handle paragraphs devoted to a single character.
        s_count["kept"] += 1

        yield p, p_speakers
