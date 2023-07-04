from os.path import join

from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.spectrum_features)
y = NpzUtils.load(MyAPI.spectrum_speakers)
y = [0 for s_name in y]

perplexies = [5, 10, 30, 50, 100]

png_path = join(MyAPI.books_storage, "features_p{preset}_all{total}".format(
    preset='-'.join([str(p) for p in perplexies]),
    total=len(X)))

plot_tsne_series(X=X, y=y, perplexies=perplexies, n_iter=1000,
                 save_png_path=png_path)
