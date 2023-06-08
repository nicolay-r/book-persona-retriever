import seaborn as sns
import pandas as pd
from collections import Counter

from matplotlib import pyplot as plt

from core.plot import draw_bar_plot
from core.spectrums import annot_spectrums_in_text
from core.utils_paragraphs import iter_paragraphs_with_n_speakers
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_my import MyAPI


def iter_paragraphs(iter_book_ids, book_by_id_func):
    for book_id in iter_book_ids:
        with open(book_by_id_func(book_id), "r") as f:
            contents = f.read()
        for paragraph in CEBApi.iter_book_paragraphs(contents):
            yield paragraph


# We connect the CEB API for our books in English,
# for which annotation of the characters has been applied.
my_api = MyAPI()
fcp_api = FcpApi()
ds_speakers = my_api.read_speakers()

speakers = annot_spectrums_in_text(
    texts_iter=map(lambda t: (t[0].Text, t[1]),
                   iter_paragraphs_with_n_speakers(
                       speakers=set(ds_speakers),
                       n_speakers=1,
                       iter_paragraphs=iter_paragraphs(
                           iter_book_ids=my_api.book_ids_from_directory(),
                           book_by_id_func=my_api.get_book_path))),
    rev_spectrums=fcp_api.reversed_spectrums())

# Compose global stat.
s_counter = Counter()
for s_ctr in speakers.values():
    for s_name, v in s_ctr.items():
        s_counter[s_name] += v

if len(s_counter) > 0:
    draw_bar_plot(s_counter,
                  x_name="bap",
                  y_name="cat",
                  val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
                  val_to_cat=lambda k: k.split('-')[0] + ' ' + str(fcp_api.find_by_id(k.split('-')[0])),
                  top_bars=50)

# Compose global stat.
s_counter = Counter()
for name, s_ctr in speakers.items():
    if len(s_ctr) > 1:
        s_counter[name] = len(s_ctr)

##################################################################
# Draw count plot of all BAPS
##################################################################
if len(s_counter) > 0:
    df_dict = {'baps_per_speaker': list(s_counter.values())}
    g = sns.displot(pd.DataFrame(df_dict), x="baps_per_speaker", kde=True)
    plt.show()