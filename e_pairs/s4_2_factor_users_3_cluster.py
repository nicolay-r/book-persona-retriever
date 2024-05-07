import json

import pandas as pd
from tqdm import tqdm

from api.my import MyAPI
from core.utils_npz import NpzUtils
from e_pairs.cfg_embeding import PairsExperimentEmbeddingConfig
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig
from embeddings.aloha.cluster import CharCluster
from embeddings.aloha.matrix import MatrixWrapper


if __name__ == '__main__':

    hla_cfg = HlaExperimentConfig(books_storage=MyAPI.books_storage)
    df = pd.read_csv(hla_cfg.hla_melted_data_filepath)
    mw = MatrixWrapper(df, user_col='user', feature_col='feature', value_col="value", use_gpu=False)
    mw.get_train(PairsExperimentEmbeddingConfig.hla_training_config, report_test=True)

    # Complete clusters for every speaker
    spectrum_cfg = SpectrumConfig()
    Y = NpzUtils.load(spectrum_cfg.speakers)
    with open(hla_cfg.hla_speaker_clusters_path, "w") as out_file:
        for speaker_index, speaker_id in tqdm(enumerate(Y), desc="Clustering speakers", total=len(Y)):
            cc = CharCluster(speaker_index, matrix_wrapper=mw)
            pos, neg = cc.retrieve(config=PairsExperimentEmbeddingConfig.hla_cluster_config)
            cluster_info = {
                "speaker_id": str(speaker_id),
                "pos": [[Y[char_ind], freq, score] for char_ind, freq, score in pos],
                "neg": [Y[neg_ind] for neg_ind in neg]
            }
            json.dump(cluster_info, out_file)
            out_file.write("\n")
