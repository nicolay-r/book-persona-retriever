import json
import os
from os.path import join

from api.ldc import LdcAPI
from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from e_pairs.cfg_hla import HlaExperimentConfig

hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
X = NpzUtils.load(hla_cfg.hla_users_embedding_factor)
category = [0] * len(X)
perplexies = [50]

png_path = join(LdcAPI.books_storage, "factor_users")
clusters_path = join(hla_cfg.hla_speaker_clusters_path)

# Visualize clustering.
limit_chars = 0
limit_pos = 40
cur_color = 1
if os.path.exists(clusters_path):
    with open(clusters_path, "r") as file_in:
        for i, line in enumerate(file_in.readlines()):
            d = json.loads(line)
            for c_id, _, _ in d["pos"][:limit_pos]:
                category[c_id] = cur_color
            cur_color += 1
            for c_id in d["neg"][:limit_pos]:
                category[c_id] = cur_color
            cur_color += 1
            if i == limit_chars:
                break

plot_tsne_series(X=X, y=category, perplexies=perplexies, n_iter=1000, show=True, alpha=0.1,
                 palette={0: "gray", 1: "green", 2: "red"})
