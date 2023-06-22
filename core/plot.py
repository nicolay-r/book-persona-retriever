from collections import Counter
from itertools import chain

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, ticker
from sklearn.manifold import TSNE
from tqdm import tqdm


def draw_bar_plot(c, x_name, y_name, val_to_x=lambda v: v,
                  val_to_cat=lambda v: 0, top_bars=None, order=True):
    assert(isinstance(c, Counter))

    df_dict = {x_name: [], y_name: [], "count": []}
    for k, v in c.most_common(top_bars if top_bars is not None else len(c)):
        df_dict[x_name].append(val_to_x(k))
        df_dict[y_name].append(val_to_cat(k))
        df_dict["count"].append(v)

    df = pd.DataFrame(df_dict)

    if order:
        df = df.sort_values("count", ascending=False)

    ax = sns.barplot(df, x="count", y=y_name, width=1)

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    plt.show()


def draw_hist_plot(c, desc, min_val=0, max_val=100, n_bins=None):
    assert(isinstance(c, Counter))

    val_width = max_val - min_val
    n_bins = abs(max_val - min_val) if n_bins is None else n_bins
    bin_width = val_width/n_bins
    #plt.xticks(np.arange(min_val + bin_width / 2, max_val + bin_width / 2, bin_width))
    plt.xticks(np.arange(min_val + bin_width, max_val + bin_width, bin_width))

    ##################################################################
    # Draw count plot of all BAPS
    ##################################################################
    df_dict = {desc: list(c.values())}
    g = sns.histplot(data=pd.DataFrame(df_dict),
                     x=desc,
                     bins=n_bins,
                     binrange=(min_val, max_val))
    plt.show()


def plot_tsne_series(X, y, perplexies=[5], n_iter=1000):

    # we need to filter due to the t-SNE limitation.
    perplexies = list(filter(lambda item: item < len(X), perplexies))

    embs_X = []
    for p in tqdm(perplexies, desc="Calc for perplexy"):
        tsne = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=p, n_iter=n_iter)
        emb_X = tsne.fit_transform(X)
        embs_X.append(emb_X)

    c1 = list(chain(*[list(embs_X[i][:, 0]) for i in range(len(perplexies))]))
    c2 = list(chain(*[list(embs_X[i][:, 1]) for i in range(len(perplexies))]))
    arr = list(chain(*[[p] * len(embs_X[0]) for p in perplexies]))

    tsne_data = pd.DataFrame()
    tsne_data["comp-1"] = c1
    tsne_data["comp-2"] = c2
    tsne_data["col"] = arr
    tsne_data["y"] = list(chain(*[y for p in perplexies]))

    g = sns.FacetGrid(tsne_data, col="col", hue="y")
    g.map(sns.scatterplot, "comp-1", "comp-2", alpha=.1)
    g.add_legend()

    plt.show()
