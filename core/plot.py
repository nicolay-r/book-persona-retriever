from collections import Counter
from itertools import chain

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, ticker
from sklearn.manifold import TSNE
from tqdm import tqdm


def colors_from_values(values, palette_name):
    # centering at 0.
    mx = max(abs(values))
    mn = -mx
    # normalize the values to range [0, 1]
    normalized = (values - mn) / (mx - mn)
    # convert to indices
    indices = np.round(normalized * (len(values) - 1)).astype(np.int32)
    # use the indices to get the colors
    palette = sns.color_palette(palette_name, len(values))
    return np.array(palette).take(indices, axis=0)


def draw_spectrum_barplot(c, x_name, y_name, val_to_x=lambda v: v, asp_hor=2, asp_ver=8,
                          val_to_cat_caption=lambda v: 0,
                          top_bars_count=None, bottom_bars_count=None,
                          order=True, show=True, save_png_path=None,
                          colorgradient="coolwarm"):
    assert(isinstance(c, Counter))

    df_dict = {x_name: [], y_name: [], "count": []}

    if top_bars_count is None and bottom_bars_count is None:
        # Keep all elements, ordered.
        items = c.most_common()
    else:
        items = []
        if top_bars_count is not None:
            # Keep top ordered.
            items += c.most_common()[:top_bars_count]
        if bottom_bars_count is not None:
            # Keep bottom ordered.
            items += c.most_common()[-bottom_bars_count:]

    k_used = set()
    for k, v in set(items):

        # Consider keys only once.
        if k in k_used:
            continue
        k_used.add(k)

        df_dict[x_name].append(val_to_x(k))
        df_dict[y_name].append(val_to_cat_caption(k))
        df_dict["count"].append(v)

    df = pd.DataFrame(df_dict)

    if order:
        df = df.sort_values("count", ascending=False)

    ax = sns.barplot(df, x="count", y=y_name, width=1,
                     palette=colors_from_values(df["count"], colorgradient))

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    if show:
        plt.show()

    if save_png_path is not None:
        # And saving the output image.
        plt.gcf().set_size_inches(asp_hor, asp_ver)
        print("Saving: {}".format(save_png_path))
        plt.savefig(save_png_path, bbox_inches='tight', dpi=200)

    plt.clf()


def draw_hist_plot(c, desc=None, min_val=None, max_val=None, n_bins=None, show=True,
                   save_png_path=None, asp_hor=8, asp_ver=2, log_scale=False):
    assert(isinstance(c, Counter))

    if min_val is None:
        min_val = int(min(c.keys()))
        for x in list(c.keys()):
            if x < min_val:
                del c[x]
    if max_val is None:
        max_val = int(max(c.keys()))
        for x in list(c.keys()):
            if x > max_val:
                del c[x]

    val_width = max_val - min_val
    n_bins = abs(max_val - min_val) if n_bins is None else n_bins
    bin_width = val_width/n_bins
    x_ticks = np.arange(min_val - bin_width, max_val + bin_width, bin_width)           
    plt.xticks(x_ticks)                         
    plt.xlim(min(x_ticks), max(x_ticks)) 

    desc = "" if desc is None else desc

    # Compose data.
    data = []
    for e, count in c.items():
        for _ in range(count):
            data.append(e)

    g = sns.histplot(data=pd.DataFrame({desc: data}),
                     x=desc,
                     bins=n_bins,
                     binrange=(min_val, max_val),
                     legend=True)

    if log_scale:
        g.set_yscale('log')

    if show:
        plt.show()

    if save_png_path is not None:
        # And saving the output image.
        plt.gcf().set_size_inches(asp_hor, asp_ver)
        print("Saving: {}".format(save_png_path))
        plt.savefig(save_png_path, bbox_inches='tight', dpi=200)

    plt.clf()


def plot_tsne_series(X, y=None, perplexies=[5], n_iter=1000, alpha=0.1, palette=None, show=False,
                     save_png_path=None):

    draw_legend = y is not None
    y = [0 for _ in range(len(X))] if y is None else y

    # we need to filter due to the t-SNE limitation.
    perplexies = list(filter(lambda item: item < len(X), perplexies))

    embs_X = []
    for p in tqdm(perplexies, desc="Calc for perplexy"):
        tsne = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=p, n_iter=n_iter)
        emb_X = tsne.fit_transform(X)
        embs_X.append(emb_X)

    c1 = list(chain(*[list(embs_X[i][:, 0]) for i in range(len(perplexies))]))
    c2 = list(chain(*[list(embs_X[i][:, 1]) for i in range(len(perplexies))]))
    perplexy_list = list(chain(*[[p] * len(embs_X[0]) for p in perplexies]))

    tsne_data = pd.DataFrame()
    tsne_data["comp-1"] = c1
    tsne_data["comp-2"] = c2
    tsne_data["perplexy"] = perplexy_list
    tsne_data["y"] = list(chain(*[y for _ in perplexies]))

    g = sns.FacetGrid(tsne_data, col="perplexy", hue="y", palette=palette, legend_out=draw_legend)
    g.map(sns.scatterplot, "comp-1", "comp-2", alpha=alpha, edgecolor=None)

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.4), ncol=1, fancybox=True, shadow=True)

    if show:
        plt.show()

    if save_png_path is not None:
        # And saving the output image.
        plt.gcf().set_size_inches(8, 6)
        print("Saving: {}".format(save_png_path))
        plt.savefig(save_png_path, bbox_inches='tight', dpi=200)
