from itertools import chain

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
from tqdm import tqdm

from core.utils_npz import NpzUtils
from utils_my import MyAPI


min_non_zero_params = 50
perplexies = [5, 10, 30, 50, 100]
n_iter = 5000

X = list(NpzUtils.load(MyAPI.spectrum_embeddings))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))
# Consider book name by default.
y = [s_name.split('_')[0] for s_name in y]
print(len(X), len(y))

# Filter by amount of non-zero components.
xy = zip(X, y)
xyf = list(filter(lambda pair: np.count_nonzero(pair[0]) > min_non_zero_params, xy))
X, y = list(zip(*xyf))
X = np.array(X)

# we need to filter due to the t-SNE limitation.
perplexies = list(filter(lambda item: item < len(X), perplexies))

embs_X = []
for p in tqdm(perplexies, desc="Calc for perplexy"):
    tsne = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=p, n_iter=n_iter)
    emb_X = tsne.fit_transform(X)
    embs_X.append(emb_X)

c1 = list(chain(*[list(embs_X[i][:, 0]) for i in range(len(perplexies))]))
c2 = list(chain(*[list(embs_X[i][:, 1]) for i in range(len(perplexies))]))
arr = list(chain(*[[p] * len(embs_X[0]) for p in perplexies]))

tsne_data = pd.DataFrame()
tsne_data["comp-1"] = c1
tsne_data["comp-2"] = c2
tsne_data["col"] = arr
tsne_data["y"] = list(chain(*[y for p in perplexies]))

g = sns.FacetGrid(tsne_data, col="col", hue="y")
g.map(sns.scatterplot, "comp-1", "comp-2", alpha=.7)
g.add_legend()

plt.show()
