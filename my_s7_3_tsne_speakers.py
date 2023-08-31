#######################################################
# Factorize
#######################################################
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
    return ceb_api.get_char_names(v)[0] + " " + pg19.find_book_title(get_book_id(v)) + " [{}]".format(v)


# Init API.
ceb_api = CEBApi()
ceb_api.read_char_map()
pg19 = PG19Api()
pg19.read()

speaker_names = list(NpzUtils.load(MyAPI.spectrum_speakers)) + list(NpzUtils.load("speaker-names.npz"))
melt_to_csv(X=list(NpzUtils.load(MyAPI.spectrum_features_norm)) + list(NpzUtils.load("speakers-selected-norm.npz")),
            y=speaker_names, out_filepath="melted_data.csv",
            user_col_name="user", feature_col_name="feature", value_col_name="value")

mw = MatrixWrapper(pd.read_csv("melted_data.csv"),
                   user_col='user', feature_col='feature', value_col="value")
mw.get_train(MyAPI.hla_training_config, report_test=False)
factors_list = []
for user_id in tqdm(range(mw.model.user_factors.shape[0])):
    factors_list.append(mw.model.user_factors[user_id])
NpzUtils.save(data=factors_list, target="x.speakers-ext-factor.npz")

plot_tsne_series(X=NpzUtils.load("x.speakers-ext-factor.npz"),
                 y=[__make_group_name(s) if s in MyAPI.predefined_speakers else "_Other" for s in speaker_names],
                 perplexies=[5], n_iter=1000, save_png_path="tsne.png", alpha=0.8,
                 palette={
                     "_Other": "gray",
                     __make_group_name(MyAPI.predefined_speakers[0]): "red",
                     __make_group_name(MyAPI.predefined_speakers[1]): "blue",
                     __make_group_name(MyAPI.predefined_speakers[2]): "green",
                     __make_group_name(MyAPI.predefined_speakers[3]): "orange",
                     __make_group_name(MyAPI.predefined_speakers[4]): "purple",
                 })
