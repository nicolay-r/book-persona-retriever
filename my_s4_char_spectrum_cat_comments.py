from collections import Counter

from core.plot import draw_bar_plot
from core.spectrums_annot import annot_spectrums_in_text
from core.utils_comments import iter_text_comments
from utils_fcp import FcpApi
from utils_my import MyAPI


fcp_api = FcpApi()
my_api = MyAPI()
speakers = my_api.read_speakers()
print("Speakers considered: {}".format(len(speakers)))

speakers = annot_spectrums_in_text(
    texts_and_speakervars_iter=iter_text_comments(speakers=set(speakers), book_path_func=my_api.get_book_path),
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
