import json
from os.path import join

import pandas as pd
from tqdm import tqdm

from core.utils_npz import NpzUtils
from embeddings.aloha.cluster import CharCluster
from embeddings.aloha.matrix import MatrixWrapper
from utils_my import MyAPI


df = pd.read_csv(join(MyAPI.books_storage, "features_melted.txt"))
mw = MatrixWrapper(df, user_col='user', feature_col='feature', value_col="value")
mw.get_train(MyAPI.hla_training_config, report_test=True)

# Complete clusters for every speaker
Y = NpzUtils.load(MyAPI.spectrum_speakers)
with open(join(MyAPI.hla_speaker_clusters_path), "w") as out_file:
    for speaker_index, speaker_id in tqdm(enumerate(Y), desc="Clustering speakers", total=len(Y)):
        cc = CharCluster(speaker_index, matrix_wrapper=mw)
        pos, neg = cc.retrieve(config=MyAPI.hla_cluster_config)
        d = {
            "speaker_id": str(speaker_id),
            "pos": [[Y[char_ind], freq, score] for char_ind, freq, score in pos],
            "neg": [Y[neg_ind] for neg_ind in neg]
        }
        json.dump(d, out_file)
        out_file.write("\n")
