from collections import Counter
from itertools import chain

from core.spectrums import annot_spectrums_in_text, annot_to_min_max_grouped
from core.utils_comments import iter_text_comments
from core.utils_npz import NpzUtils
from core.utils_paragraphs import iter_paragraphs_with_n_speakers
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_my import MyAPI


def iter_all(speakers):

    # Iterate over paragraphs.
    paragraphs_it = map(
        lambda t: (t[0].Text, t[1]),
        iter_paragraphs_with_n_speakers(
            speakers=set(speakers),
            n_speakers=1,
            iter_paragraphs=CEBApi.iter_paragraphs(
                iter_book_ids=my_api.book_ids_from_directory(),
                book_by_id_func=my_api.get_book_path)))

    # Iterate over comments.
    comments_it = iter_text_comments(
        speakers=set(speakers),
        book_path_func=my_api.get_book_path)

    return chain(paragraphs_it, comments_it)


my_api = MyAPI()
fcp_api = FcpApi()
speaker_spectrums_dict = annot_spectrums_in_text(
    texts_iter=iter_all(speakers=my_api.read_speakers()),
    rev_spectrums=fcp_api.reversed_spectrums())

# Saving.
x, y = [], []
d = annot_to_min_max_grouped(speaker_spectrums_dict,
                             do_norm=True,
                             as_vectors=True,
                             spectrums_count=len(fcp_api._lexicon)+1)

for s_name, s_ctr in d.items():
    x.append(s_ctr)
    y.append(s_name)

NpzUtils.save(data=x, target=MyAPI.spectrum_embeddings)
NpzUtils.save(data=y, target=MyAPI.spectrum_speakers)
