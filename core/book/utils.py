from collections import Counter

from tqdm import tqdm

from core.book.paragraph import Paragraph
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def iter_paragraphs_with_n_speakers(speakers, iter_paragraphs, n_speakers=1, multi_mentions=False):
    """ Iterate text paragraphs which contains only N mentioned speakers
        based on the Character-based-embedding API.

        NOTE:
        * This method excluded cases with such speakers that mentioned in paragraph but not mentioned in `speakers`
        * It is important that each speaker represent in a form of separated word /
            or speaker recognition function support this case.
    """
    assert(isinstance(speakers, set))

    s_count = Counter()
    pbar = tqdm(iter_paragraphs, "Iter Paragraphs")
    for p in pbar:
        assert(isinstance(p, Paragraph))

        pbar.set_postfix({
            'kept': s_count["kept"],
            'total': s_count['total']
        })

        s_count["total"] += 1

        terms = p.Text.split()

        p_speakers = []
        has_others = False
        for term in terms:

            # TODO. This is expected to be an outer function.
            if not GuttenbergDialogApi.is_character(term):
                continue

            if term[0] == '{' and term[-1] == '}':
                term = term[1:-1]

            if CEBApi.speaker_variant_to_speaker(term) in speakers:
                p_speakers.append(term)
            else:
                has_others = True

        # Cast to set and back in the case if `use_set` flag is raised.
        p_speakers = list(set(p_speakers)) if multi_mentions else p_speakers

        if len(p_speakers) != n_speakers or has_others:
            continue

        # handle paragraphs devoted to a single character.
        s_count["kept"] += 1

        yield p, p_speakers
