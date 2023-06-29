import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from utils_my import MyAPI

u_lens = []
for line in MyAPI.read_dataset(MyAPI.dataset_filepath):

    if line is None:
        continue

    # split and remove meta information.
    terms = line.split(' ')[1:]
    u_lens.append(len(terms))

data = pd.DataFrame({"utt_lens": u_lens})
g = sns.displot(data, x="utt_lens", kde=True, fill=True)

#plt.ylim(0, 2500)
#plt.xlim(0, 100)
plt.show()
