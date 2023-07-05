import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from utils_my import MyAPI

u_lens = []
for args in MyAPI.read_dataset(MyAPI.dataset_filepath, split_meta=True):

    if args is None:
        continue

    meta, text = args
    # split and remove meta information.
    u_lens.append(len(text.split(' ')))

data = pd.DataFrame({"utt_lens": u_lens})
g = sns.displot(data, x="utt_lens", kde=True, fill=True)

plt.show()
