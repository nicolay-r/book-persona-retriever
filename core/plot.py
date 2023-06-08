from collections import Counter

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, ticker


def draw_bar_plot(c, x_name, cat_name, val_to_x=lambda v: v,
                  val_to_cat=lambda v: 0, top_bars=None, order=True):
    assert(isinstance(c, Counter))

    df_dict = {x_name: [], cat_name: [], "val": []}
    for k, v in c.most_common(top_bars if top_bars is not None else len(c)):
        df_dict[x_name].append(val_to_x(k))
        df_dict[cat_name].append(val_to_cat(k))
        df_dict["val"].append(v)

    df = pd.DataFrame(df_dict)

    if order:
        df = df.sort_values("val", ascending=False)

    ax = sns.barplot(df, x="val", y=cat_name, width=1)

    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    plt.show()
