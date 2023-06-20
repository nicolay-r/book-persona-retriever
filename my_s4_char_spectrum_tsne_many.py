from itertools import chain

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.manifold import TSNE

from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.spectrum_embeddings)
y = NpzUtils.load(MyAPI.spectrum_speakers)

perplexies = [5, 10, 30, 50, 100]
n_iter = 1000

embs_X = []
for p in perplexies:
    tsne = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=p,
                n_iter=n_iter)
    emb_X = tsne.fit_transform(X)
    embs_X.append(emb_X)

tsne_data = pd.DataFrame()
c1 = list(chain(*[list(embs_X[i][:, 0]) for i in range(len(perplexies))]))
c2 = list(chain(*[list(embs_X[i][:, 1]) for i in range(len(perplexies))]))
arr = list(chain(*[[p] * len(embs_X[0]) for p in perplexies]))
tsne_data["comp-1"] = c1
tsne_data["comp-2"] = c2
tsne_data["col"] = arr

g = sns.FacetGrid(tsne_data, col="col")
g.map(sns.scatterplot, "comp-1", "comp-2", alpha=.7)
g.add_legend()

plt.show()
