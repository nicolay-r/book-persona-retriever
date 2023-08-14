from itertools import chain

from core.book.utils import iter_paragraphs_with_n_speakers
from core.dialogue.comments import filter_relevant_text_comments
from core.spectrums_annot import annot_spectrums_in_text, annot_to_min_max_grouped
from core.utils_npz import NpzUtils
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_all(speakers):

    # Iterate over paragraphs.
    paragraphs_it = map(
        lambda t: (t[0].Text, t[1]),
        iter_paragraphs_with_n_speakers(
            speakers=set(speakers),
            n_speakers=MyAPI.spectrum_speakers_in_paragraph,
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


my_api = MyAPI()
fcp_api = FcpApi()
speaker_spectrums_dict = annot_spectrums_in_text(
    texts_and_speakervars_iter=iter_all(speakers=my_api.read_speakers()),
    rev_spectrums=fcp_api.reversed_spectrums())

# Saving.
spectrums_count = len(fcp_api._lexicon)+1
data = {
    MyAPI.spectrum_features_norm: lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count),
    MyAPI.spectrum_features_diff: lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count),
}

for x_path, f in data.items():
    x, y = [], []
    d = f(speaker_spectrums_dict)

    for s_name, s_ctr in d.items():
        x.append(s_ctr)
        y.append(s_name)

    NpzUtils.save(data=x, target=x_path)
    NpzUtils.save(data=y, target=MyAPI.spectrum_speakers)
