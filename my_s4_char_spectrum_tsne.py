from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.spectrum_features)
y = NpzUtils.load(MyAPI.spectrum_speakers)
y = [0 for s_name in y]
plot_tsne_series(X=X, y=y, perplexies=[50], n_iter=1000)
