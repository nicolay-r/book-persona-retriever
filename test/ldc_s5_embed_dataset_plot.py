from os.path import join

import numpy as np

from api.ldc import LdcAPI
from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils


def __tsne_plot(X, save_prefix):
    perplexies = [50]
    png_path = join(LdcAPI.books_storage, "{prefix}_p{preset}_all{total}".format(
        prefix=save_prefix,
        preset='-'.join([str(p) for p in perplexies]),
        total=len(X)))
    plot_tsne_series(X=np.array(X), perplexies=perplexies, n_iter=1000, palette={0: "purple"}, alpha=0.04,
                     save_png_path=png_path)


if __name__ == '__main__':

    __tsne_plot(X=list(NpzUtils.load(LdcAPI.dataset_st_embedding_query)), save_prefix="dataset_query")
    __tsne_plot(X=list(NpzUtils.load(LdcAPI.dataset_st_embedding_response)), save_prefix="dataset_response")
