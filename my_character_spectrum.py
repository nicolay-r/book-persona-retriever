import seaborn as sns
import pandas as pd
from collections import Counter

from matplotlib import pyplot as plt
from tqdm import tqdm

from utils import Paragraph
from utils_fcp import FcpApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI
from utils_ceb import CEBApi


gd_api = GuttenbergDialogApi()


def annot_spectrums_in_text(texts_iter, rev_spectrums):
    assert(isinstance(spectrums, dict))

    c = Counter()
    for text in texts_iter:
        norm_terms = gd_api.normalize_terms(text.split())
        for term in norm_terms:
            if term in rev_spectrums:
                s = rev_spectrums[term]
                bap = "{}-{}".format(s["class"], s["type"])
                c[bap] += 1

    return c


def iter_paragraphs_with_n_speakers(n_speakers=1):

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

            chars = []
            for t in terms:
                if GuttenbergDialogApi.is_character(t):
                    chars.append(t)

            if len(chars) != n_speakers:
                continue

            # handle paragraphs devoted to a single character.
            kept += 1

            yield p

    print(kept)
    print("Filtered: {}".format(round(kept * 100.0 / total, 2)))


# We connect the CEB API for our books in English,
# for which annotation of the characters has been applied.
ceb_api = CEBApi(books_root=MyAPI.books_storage_en)
fcp_api = FcpApi()
spectrums = fcp_api.extract_as_lexicon()

print(spectrums)

# Reversed spectrums.
rev_spectrums = {}
for s_type, value_d in spectrums.items():
    l = value_d["low"].pop()
    h = value_d["high"].pop()
    if l not in rev_spectrums:
        rev_spectrums[l] = {"class": s_type, "type": "low"}
    if h not in rev_spectrums:
        rev_spectrums[h] = {"class": s_type, "type": "high"}

c = annot_spectrums_in_text(
    texts_iter=map(lambda p: p.Text, iter_paragraphs_with_n_speakers()),
    rev_spectrums=rev_spectrums)

print(c)

df_dict = {'bap': [], 'cat': []}
for k, v in c.items():
    for i in range(v):
        bap_index = int(''.join([ch for ch in k if ch.isdigit()]))
        category = k.split('-')[1]
        df_dict["bap"].append(bap_index)
        df_dict["cat"].append(category)
g = sns.displot(pd.DataFrame(df_dict), x="bap", hue="cat", kde=True)

#ax = g.axes[0, 0]
#ax.set_xticks(range(300))
#ax.set_xticklabels(range(300))
plt.show()
