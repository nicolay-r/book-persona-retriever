import pandas as pd
from tqdm import tqdm

from core.utils_npz import NpzUtils
from embeddings.aloha.matrix import MatrixWrapper
from utils_my import MyAPI


df = pd.read_csv(MyAPI.hla_melted_data_filepath)
mw = MatrixWrapper(df, user_col='user', feature_col='feature', value_col="value")
mw.get_train(MyAPI.hla_training_config, report_test=False)

# Save the result model.
x = []
for user_id in tqdm(range(mw.model.user_factors.shape[0])):
    x.append(mw.model.user_factors[user_id])

NpzUtils.save(data=x, target=MyAPI.hla_users_embedding_factor)
