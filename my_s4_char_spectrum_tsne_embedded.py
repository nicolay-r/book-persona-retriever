from core.plot import plot_tsne_series
from core.spectrums_emb import FILTER_PRESETS
from core.utils_npz import NpzUtils
from utils_my import MyAPI


X = list(NpzUtils.load(MyAPI.spectrum_st_embeddings.format(preset=MyAPI.spectrum_default_preset)))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

# Blank painting.
y = [0 for s_name in y]

print("Origin:", len(X))

# Filter by amount of non-zero components.
X, y = FILTER_PRESETS["all-no-color"](X, y)

print("Filtered:", len(X))
print("V-size: {}".format(len(X[0])))

plot_tsne_series(X=X, y=y, perplexies=[5, 10, 30, 50, 100], n_iter=1000)
