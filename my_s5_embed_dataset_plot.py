import numpy as np

from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.dataset_st_embedding_query))

# Blank painting.
for x in X:
    print(x)

plot_tsne_series(X=np.array(X), perplexies=[5], n_iter=1000, palette={0: "purple"}, alpha=0.08)
