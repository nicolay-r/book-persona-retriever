#######################################################
# Factorize
#######################################################
from os.path import join

import numpy as np
import pandas as pd
from tqdm import tqdm

from core.factor.utils import melt_to_csv
from core.plot import plot_tsne_series
from core.utils_npz import NpzUtils
from embeddings.aloha.matrix import MatrixWrapper
from utils_ceb import CEBApi
from utils_my import MyAPI
from utils_pg19 import PG19Api


def get_book_id(v):
    return v.split('_')[0]


def __make_group_name(v):
    return ceb_api.get_char_names(v)[0] + " " + \
           '"{}"'.format(pg19.find_book_title(get_book_id(v)))
           #" [{}]".format(v)


# Init API.
ceb_api = CEBApi()
ceb_api.read_char_map()
pg19 = PG19Api()
pg19.read()

# Original data.
speaker_names = list(NpzUtils.load(join(MyAPI.selected_output_dir, "speaker-all-names.npz"))) + \
                list(NpzUtils.load(join(MyAPI.selected_output_dir, "speaker-selected-names.npz")))
X = list(NpzUtils.load(join(MyAPI.selected_output_dir, "speakers-all-norm.npz"))) + \
    list(NpzUtils.load(join(MyAPI.selected_output_dir, "speakers-selected-norm.npz")))

# Filtering unique. (because of the manually selected speakers, they might be a part of the valid/train set.
# This is temporary caused due to the lack of fixed sort at dataset creation stage (already fixed).
sset = set()
u_speaker_names = []
u_X = []
for i, s in enumerate(speaker_names):
    if s in sset:
        print("Skipped: {}".format(s))
        continue
    print(np.count_nonzero(X[i]))
    if np.count_nonzero(X[i]) < 5:
        continue
    sset.add(s)
    u_speaker_names.append(s)
    u_X.append(X[i])

melted_filepath = join(MyAPI.selected_output_dir, "melted_data.csv")
melt_to_csv(X=u_X, y=u_speaker_names, out_filepath=melted_filepath,
            user_col_name="user", feature_col_name="feature", value_col_name="value")

mw = MatrixWrapper(pd.read_csv(melted_filepath),
                   user_col='user', feature_col='feature', value_col="value")
mw.get_train(MyAPI.hla_training_config, report_test=False)
factors_list = []
for user_id in tqdm(range(mw.model.user_factors.shape[0])):
    factors_list.append(mw.model.user_factors[user_id])
factor_path = join(MyAPI.selected_output_dir, "x.speakers-ext-factor.npz")
NpzUtils.save(data=factors_list, target=factor_path)
plot_tsne_series(X=NpzUtils.load(factor_path),
                 y=[__make_group_name(s) if s in MyAPI.predefined_speakers else "_Other"
                    for s in u_speaker_names],
                 perplexies=[5], n_iter=3000,
                 save_png_path=join(MyAPI.selected_output_dir, "tsne.png"),
                 alpha=0.15,
                 palette={
                     "_Other": "gray",
                     __make_group_name(MyAPI.predefined_speakers[0]): "red",
                     __make_group_name(MyAPI.predefined_speakers[1]): "blue",
                     __make_group_name(MyAPI.predefined_speakers[2]): "green",
                     __make_group_name(MyAPI.predefined_speakers[3]): "orange",
                     __make_group_name(MyAPI.predefined_speakers[4]): "purple",
                 })
