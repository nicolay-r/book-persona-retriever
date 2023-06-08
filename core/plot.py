from collections import Counter

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, ticker


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
