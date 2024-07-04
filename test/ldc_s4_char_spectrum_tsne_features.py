from os.path import join

from api.ldc import LdcAPI
from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from e_pairs.cfg_spectrum import SpectrumConfig


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig()
    X = NpzUtils.load(spectrum_cfg.features_norm)
    y = NpzUtils.load(spectrum_cfg.speakers)
    y = [0 for s_name in y]

    perplexies = [5, 10, 30, 50, 100]

    png_path = join(LdcAPI.books_storage, "features_p{preset}_all{total}".format(
        preset='-'.join([str(p) for p in perplexies]),
        total=len(X)))

    plot_tsne_series(X=X, y=y, perplexies=perplexies, n_iter=1000,
                     save_png_path=png_path)
