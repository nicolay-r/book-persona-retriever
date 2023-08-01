from collections import Counter

from tqdm import tqdm

from core.book.paragraph import Paragraph
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def iter_paragraphs_with_n_speakers(speakers, iter_paragraphs, n_speakers=1):
    """ Iterate text paragraphs which contains only N mentioned speakers
        based on the Character-based-embedding API.
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
        for term in terms:
            if not GuttenbergDialogApi.is_character(term):
                continue

            if term[0] == '{' and term[-1] == '}':
                term = term[1:-1]

            if CEBApi.speaker_variant_to_speaker(term) in speakers:
                p_speakers.append(term)

        if len(p_speakers) != n_speakers:
            continue

        # handle paragraphs devoted to a single character.
        s_count["kept"] += 1

        yield p, p_speakers
