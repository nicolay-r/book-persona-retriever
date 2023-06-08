import pandas as pd
import seaborn as sns

from collections import Counter

from matplotlib import pyplot as plt

from core.plot import draw_bar_plot
from core.spectrums import annot_spectrums_in_text
from utils_fcp import FcpApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_text_comments():
    my_api = MyAPI()
    g_api = GuttenbergDialogApi()
    for k in range(3):

        it = g_api.filter_comment_with_speaker_at_k(
            book_path_func=my_api.get_book_path, k=k)

        for book_id, comments in it:
            for comment in comments:

                # Seek for speaker in a comment.
                speaker = None
                for term in comment.split():
                    if GuttenbergDialogApi.is_character(term):
                        speaker = term

                yield comment, speaker


fcp_api = FcpApi()
speakers = annot_spectrums_in_text(texts_iter=iter_text_comments(),
                                   rev_spectrums=fcp_api.reversed_spectrums())


# Compose global stat.
s_counter = Counter()
for s_ctr in speakers.values():
    for s_name, v in s_ctr.items():
        s_counter[s_name] += v

draw_bar_plot(s_counter, x_name="bap", cat_name="cat",
              val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
              # BAP + meaning
              val_to_cat=lambda k: k.split('-')[0] + ' ' + str(fcp_api.find_by_id(k.split('-')[0])),
              top_bars=25)

# Compose global stat.
s_counter = Counter()
for name, s_ctr in speakers.items():
    if len(s_ctr) > 1:
        s_counter[name] = len(s_ctr)

##################################################################
# Draw count plot of all BAPS
##################################################################
df_dict = {'baps_per_speaker': list(s_counter.values())}
g = sns.displot(pd.DataFrame(df_dict), x="baps_per_speaker", kde=True)
plt.show()