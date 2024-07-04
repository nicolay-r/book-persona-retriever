from os.path import join

from api.ldc import LdcAPI
from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from e_pairs.cfg_hla import HlaExperimentConfig


if __name__ == '__main__':

    hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
    X = NpzUtils.load(hla_cfg.hla_users_embedding_factor)

    perplexies = [5]

    png_path = join(LdcAPI.books_storage, "factor_users")
    plot_tsne_series(X=X, y=[0] * len(X), perplexies=perplexies, n_iter=1000, save_png_path=png_path)
