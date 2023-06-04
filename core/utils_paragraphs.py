from tqdm import tqdm

from utils import Paragraph
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi


def iter_paragraphs_with_n_speakers(n_speakers=1):
    """ Iterate text paragraphs which contains only N mentioned speakers
        based on the Character-based-embedding API.
    """

    ceb_api = CEBApi()

    kept = 0
    total = 0
    for book_id in tqdm(ceb_api.book_ids_from_directory(), desc="Reading books"):

        # Read book contents.
        with open(ceb_api.get_book_path(book_id), "r") as f:
            contents = f.read()

        # Iterate book by paragraphs.
        # Tip: we consider that one paragraph consist only one person discussion.
        for p in ceb_api.iter_book_paragraphs(contents):
            assert (isinstance(p, Paragraph))

            total += 1
            terms = p.Text.split()

            speakers = []
            for t in terms:
                if GuttenbergDialogApi.is_character(t):
                    speakers.append(t)

            if len(speakers) != n_speakers:
                continue

            # handle paragraphs devoted to a single character.
            kept += 1

            yield p, speakers

    print(kept)
    print("Filtered: {}".format(round(kept * 100.0 / total, 2)))
