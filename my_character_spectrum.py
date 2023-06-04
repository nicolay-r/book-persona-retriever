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
spectrums = fcp_api.extract_as_lexicon()

# Reversed spectrums.
rev_spectrums = {}
for s_type, value_d in spectrums.items():
    l = value_d["low"].pop()
    h = value_d["high"].pop()
    if l not in rev_spectrums:
        rev_spectrums[l] = {"class": s_type, "type": "low"}
    if h not in rev_spectrums:
        rev_spectrums[h] = {"class": s_type, "type": "high"}

speakers = annot_spectrums_in_text(
    texts_iter=map(lambda t: (t[0].Text, t[1]), iter_paragraphs_with_n_speakers()),
    rev_spectrums=rev_spectrums)

# Compose global stat.
c = Counter()
for s_ctr in speakers.values():
    for k, v in s_ctr.items():
        c[k] += v

draw_count_plot(c, x_name="bap", cat_name="cat",
                val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
                val_to_cat=lambda k: k.split('-')[1],
                interval=10)

# Compose global stat.
c = Counter()
for name, s_ctr in speakers.items():
    if len(s_ctr) > 1:
        c[name] = len(s_ctr)

##################################################################
# Draw count plot of all BAPS
##################################################################
df_dict = {'baps_per_speaker': list(c.values())}
g = sns.displot(pd.DataFrame(df_dict), x="baps_per_speaker", kde=True)
plt.show()