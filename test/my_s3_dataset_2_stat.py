import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from utils_my import MyAPI

utterances_lengths = []
for args in MyAPI.read_dataset(MyAPI.dataset_filepath, split_meta=True):

    if args is None:
        continue

    meta, text = args
    # split and remove meta information.
    utterances_lengths.append(len(text.split(' ')))

data = pd.DataFrame({"utt_lens": utterances_lengths})
g = sns.displot(data, x="utt_lens", kde=True, fill=True)

plt.show()
