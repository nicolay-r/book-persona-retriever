import pandas as pd
from tqdm import tqdm

from api.ldc import LdcAPI
from core.utils_npz import NpzUtils
from e_pairs.cfg_embeding import PairsExperimentEmbeddingConfig
from e_pairs.cfg_hla import HlaExperimentConfig
from embeddings.aloha.matrix import MatrixWrapper


if __name__ == '__main__':

    hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
    df = pd.read_csv(hla_cfg.hla_melted_data_filepath)
    # NOTE: We force disable GPU support in order to perform NpzUtils.save correctly.
    mw = MatrixWrapper(df, user_col='user', feature_col='feature', value_col="value", use_gpu=False)
    mw.get_train(PairsExperimentEmbeddingConfig.hla_training_config, report_test=False)

    # Save the result model.
    x = []
    for user_id in tqdm(range(mw.model.user_factors.shape[0])):
        x.append(mw.model.user_factors[user_id])

    NpzUtils.save(data=x, target=hla_cfg.hla_users_embedding_factor)
