import seaborn as sns
import pandas as pd
from collections import Counter

from matplotlib import pyplot as plt

from core.plot import draw_count_plot
from core.spectrums import annot_spectrums_in_text
from core.utils_paragraphs import iter_paragraphs_with_n_speakers
from utils_fcp import FcpApi
from utils_my import MyAPI
from utils_ceb import CEBApi


# We connect the CEB API for our books in English,
# for which annotation of the characters has been applied.
ceb_api = CEBApi(books_root=MyAPI.books_storage_en)
fcp_api = FcpApi()

speakers = annot_spectrums_in_text(
    texts_iter=map(lambda t: (t[0].Text, t[1]), iter_paragraphs_with_n_speakers()),
    rev_spectrums=fcp_api.reversed_spectrums())

# Compose global stat.
s_counter = Counter()
for s_ctr in speakers.values():
    for s_name, v in s_ctr.items():
        s_counter[s_name] += v

draw_count_plot(s_counter, x_name="bap", cat_name="cat",
                val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
                val_to_cat=lambda k: k.split('-')[1],
                interval=10)

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