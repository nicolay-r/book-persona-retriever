from collections import Counter

from core.plot import draw_bar_plot
from core.spectrums import annot_spectrums_in_text
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_text_comments(speakers, book_path_func):
    assert(isinstance(speakers, set))
    assert(callable(book_path_func))

    g_api = GuttenbergDialogApi()
    for k in range(3):

        for book_id, comments in g_api.filter_comment_with_speaker_at_k(book_path_func=book_path_func, k=k):
            for comment in comments:
                # Seek for speaker in a comment.
                for term in comment.split():
                    if GuttenbergDialogApi.is_character(term):
                        if CEBApi.speaker_variant_to_speaker(term) in speakers:
                            yield comment, term
                            break


fcp_api = FcpApi()
my_api = MyAPI()
speakers = my_api.read_speakers()
print("Speakers considered: {}".format(len(speakers)))

speakers = annot_spectrums_in_text(
    texts_iter=iter_text_comments(speakers=set(speakers),
                                  book_path_func=my_api.get_book_path),
    rev_spectrums=fcp_api.reversed_spectrums())


# Compose global stat.
s_counter = Counter()
for s_ctr in speakers.values():
    for s_name, v in s_ctr.items():
        s_counter[s_name] += v

if len(s_counter) != 0:
    draw_bar_plot(s_counter,
                  x_name="bap",
                  y_name="cat",
                  val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
                  # BAP + meaning
                  val_to_cat=lambda k: k.split('-')[0] + ' ' + str(fcp_api.find_by_id(k.split('-')[0])),
                  top_bars=50)
