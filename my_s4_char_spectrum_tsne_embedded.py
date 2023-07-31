from os.path import join

from core.plot import plot_tsne_series
from core.spectrums.presets import FILTER_PRESETS
from core.utils_npz import NpzUtils
from utils_my import MyAPI

preset = MyAPI.spectrum_default_preset
X = NpzUtils.load(MyAPI.spectrum_st_embeddings.format(preset=preset))
y = NpzUtils.load(MyAPI.spectrum_speakers)

# Blank painting.
y = [0 for s_name in y]

print("Origin:", len(X))

# Filter by amount of non-zero components.
X, y = FILTER_PRESETS["all-no-color"](X, y)

print("Filtered:", len(X))
print("V-size: {}".format(len(X[0])))

perplexies=[5, 10, 30, 50, 100]

png_path = join(MyAPI.books_storage, "embedded_{preset}_p{prompt}_all{total}".format(
    preset=preset,
    prompt='-'.join([str(p) for p in perplexies]),
    total=len(X)))

plot_tsne_series(X=X, y=y, perplexies=perplexies, n_iter=1000, save_png_path=png_path)
