import numpy as np
import pandas as pd
from core.plot import plot_tsne_series

groups = {
    'g1': ['Xiren', 'Wangfuren', 'Qinkeqin'],
    'g2': ['Jiabaoyu', 'Liwan', 'Jiatanchun'],
    'g3': ['Lindaiyu', 'Qingwen', 'Xingfuren'],
    'g4': ['Miaoyu', 'Jiaxichun', 'Xuebaochai'],
    'g5': ['Youerjie', 'Shixiangyun', 'Jiayinchun'],
}


# explicit function to normalize array
def normalize(arr, t_min, t_max):
    norm_arr = []
    diff = t_max - t_min
    diff_arr = max(arr) - min(arr)   
    for i in arr:
        temp = (((i - min(arr))*diff)/diff_arr) + t_min
        norm_arr.append(temp)
    return norm_arr


def __find_group(name):
    assert(isinstance(name, str))
    for k, v in groups.items():
        if name in v:
            # group name.
            return ",".join(v)
    return "_Other"


df = pd.read_csv("../data/LCPM.csv")

X = []
y = []
for i, r in df.iterrows():
    X.append(normalize(np.array(r[1:]), 0, 1))
    y.append(r[0])

print(X)
X = np.array(X)
plot_tsne_series(X=X, y=[__find_group(i) for i in y], perplexies=[2], n_iter=1000, alpha=0.7,
                 palette={
                    "_Other": "gray",
                    ','.join(groups["g1"]): "red",
                    ','.join(groups["g2"]): "blue",
                    ','.join(groups["g3"]): "green",
                    ','.join(groups["g4"]): "orange",
                    ','.join(groups["g5"]): "purple",
                 })
