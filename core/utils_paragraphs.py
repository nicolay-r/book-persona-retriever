from collections import Counter

from tqdm import tqdm

from utils import Paragraph
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def iter_paragraphs_with_n_speakers(considered_speakers, n_speakers=1):
    """ Iterate text paragraphs which contains only N mentioned speakers
        based on the Character-based-embedding API.
    """
    assert(isinstance(considered_speakers, set))

    ceb_api = CEBApi()

    s_count = Counter()
    pbar = tqdm(ceb_api.book_ids_from_directory(), desc="Reading books")
    for book_id in pbar:

        # Read book contents.
        with open(ceb_api.get_book_path(book_id), "r") as f:
            contents = f.read()

        # Iterate book by paragraphs.
        # Tip: we consider that one paragraph consist only one person discussion.
        for p in ceb_api.iter_book_paragraphs(contents):
            assert (isinstance(p, Paragraph))

            pbar.set_postfix({
                'kept': s_count["kept"],
                'total': s_count['total']
            })

            s_count["total"] += 1

            terms = p.Text.split()

            speakers = []
            for term in terms:
                if GuttenbergDialogApi.is_character(term):
                    speaker_id = CEBApi.speaker_variant_to_speaker(term)
                    if speaker_id in considered_speakers:
                        speakers.append(term)

            if len(speakers) != n_speakers:
                continue

            # handle paragraphs devoted to a single character.
            s_count["kept"] += 1

            yield p, speakers