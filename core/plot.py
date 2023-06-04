from collections import Counter

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, ticker


def draw_count_plot(c, x_name, cat_name, val_to_x=lambda v: v, val_to_cat=lambda v: 0, interval=10):
    """ Draw count plot of all BAPS
    """
    assert(isinstance(c, Counter))

    df_dict = {x_name: [], cat_name: []}
    for k, v in c.items():
        for i in range(v):
            print(k)
            df_dict[x_name].append(val_to_x(k))
            df_dict[cat_name].append(val_to_cat(k))
    ax = sns.countplot(pd.DataFrame(df_dict), x=x_name, hue=cat_name, width=1)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(interval))
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())

    plt.show()
