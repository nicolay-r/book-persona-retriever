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

    d = {}
    for text, speakers in texts_iter:
        norm_terms = gd_api.normalize_terms(text.split())

        # We limit only for a single speaker.
        speaker = speakers[0]

        for term in norm_terms:
            if term in rev_spectrums:
                s = rev_spectrums[term]
                bap = "{}-{}".format(s["class"], s["type"])
                if speaker not in d:
                    d[speaker] = Counter()
                d[speaker][bap] += 1

    return d


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

            speakers = []
            for t in terms:
                if GuttenbergDialogApi.is_character(t):
                    speakers.append(t)

            if len(speakers) != n_speakers:
                continue

            # handle paragraphs devoted to a single character.
            kept += 1

            yield p, speakers

    print(kept)
    print("Filtered: {}".format(round(kept * 100.0 / total, 2)))


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

##################################################################
# Draw count plot of all BAPS
##################################################################
df_dict = {'bap': [], 'cat': []}
for k, v in c.items():
    for i in range(v):
        bap_index = int(''.join([ch for ch in k if ch.isdigit()]))
        category = k.split('-')[1]
        df_dict["bap"].append(bap_index)
        df_dict["cat"].append(category)
g = sns.countplot(pd.DataFrame(df_dict), x="bap", hue="cat")
plt.show()

print(c)

# Compose global stat.
c = Counter()
for name, s_ctr in speakers.items():
    if len(s_ctr) > 1:
        c[name] = len(s_ctr)

##################################################################
# Draw count plot of all BAPS
##################################################################
df_dict = {'baps_per_speaker': list(c.values())}
g = sns.displot(pd.DataFrame(df_dict), x="baps_per_speaker", kind="kde")
plt.show()

print(c)