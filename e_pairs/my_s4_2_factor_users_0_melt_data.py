from core.factor.utils import melt_to_csv
from core.utils_npz import NpzUtils
from utils_my import MyAPI


melt_to_csv(X=list(NpzUtils.load(MyAPI.spectrum_features_norm)),
            y=list(NpzUtils.load(MyAPI.spectrum_speakers)),
            out_filepath=MyAPI.hla_melted_data_filepath,
            user_col_name="user", feature_col_name="feature", value_col_name="value")
