from collections import Counter

from core.dialogue.comments import filter_relevant_text_comments
from core.plot import draw_bar_plot
from core.spectrums_annot import annot_spectrums_in_text
from utils_fcp import FcpApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


fcp_api = FcpApi()
speakers = MyAPI.read_speakers()
print("Speakers considered: {}".format(len(speakers)))

my_api = MyAPI()
g_api = GuttenbergDialogApi()
speakers = annot_spectrums_in_text(
    texts_and_speakervars_iter=filter_relevant_text_comments(
        is_term_speaker_func=GuttenbergDialogApi.is_character,
        speaker_positions=MyAPI.spectrum_comment_speaker_positions,
        iter_comments_at_k_func=lambda k: g_api.filter_comment_with_speaker_at_k(
            book_path_func=my_api.get_book_path, k=k),
        speakers=set(speakers)),
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
                  top_bars=40)
