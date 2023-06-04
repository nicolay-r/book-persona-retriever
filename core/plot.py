from collections import Counter

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def draw_count_plot(c, x_name, cat_name, val_to_x=lambda v: v, val_to_cat=lambda v: 0):
    """ Draw count plot of all BAPS
    """
    assert(isinstance(c, Counter))

    df_dict = {x_name: [], cat_name: []}
    for k, v in c.items():
        for i in range(v):
            print(k)
            df_dict[x_name].append(val_to_x(k))
            df_dict[cat_name].append(val_to_cat(k))
    sns.countplot(pd.DataFrame(df_dict), x=x_name, hue=cat_name)

    plt.show()
