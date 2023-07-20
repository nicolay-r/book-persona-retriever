from os.path import join

import implicit
import pandas as pd
from implicit.evaluation import coo_matrix

from core.utils_npz import NpzUtils
from utils_my import MyAPI


def dataframe_to_coo(data, col1, col2, col3):
    cat1 = data[col1].astype('category')
    cat2 = data[col2].astype('category')
    coo = coo_matrix((data[col3], (cat2.cat.codes.copy(), cat1.cat.codes.copy())))
    return coo, cat1, cat2


df = pd.read_csv(join(MyAPI.books_storage, "features_melted.txt"))
coo, cat1, cat2 = dataframe_to_coo(df, "feature", "user", "value")

# conf_scale: scale up the matrix with a confidence integer.
conf_scale = 30
model = implicit.als.AlternatingLeastSquares(factors=30, regularization=0.1, iterations=500)
model.fit(coo * conf_scale)

# Save the result model.
x = []
for user_id in range(model.user_factors.shape[0]):
    x.append(model.user_factors[user_id])

NpzUtils.save(data=x, target=MyAPI.users_embedding_factor)
