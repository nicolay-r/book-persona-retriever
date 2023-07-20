from os.path import join

from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.users_embedding_factor)

perplexies = [5]

png_path = join(MyAPI.books_storage, "factor_users")
plot_tsne_series(X=X, y=[0] * len(X), perplexies=perplexies, n_iter=1000, save_png_path=png_path)
