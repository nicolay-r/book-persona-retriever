import json
import os
from os.path import join

from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.users_embedding_factor)
category = [0] * len(X)
perplexies = [50]

png_path = join(MyAPI.books_storage, "factor_users")
clusters_path = join(MyAPI.books_storage, "clusters.jsonl")

# Visualize clustering.
limit_chars = 1
limit_pos = 20
if os.path.exists(clusters_path):
    with open(clusters_path, "r") as file_in:
        for i, line in enumerate(file_in.readlines()):
            d = json.loads(line)
            pos = d["pos"]
            for c_id, _, _ in pos[:limit_pos]:
                category[c_id] = i + 1
            print("color {}".format(i))
            if i == limit_chars:
                break

plot_tsne_series(X=X, y=category, perplexies=perplexies, n_iter=5000, show=True, alpha=0.2)
