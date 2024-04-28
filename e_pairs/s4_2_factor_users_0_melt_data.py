from core.factor.utils import melt_to_csv
from core.utils_npz import NpzUtils
from e_pairs.cfg_spectrum import SpectrumConfig
from utils_my import MyAPI


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig(books_storage=MyAPI.books_storage)
    melt_to_csv(X=list(NpzUtils.load(spectrum_cfg.features_norm)),
                y=list(NpzUtils.load(spectrum_cfg.speakers)),
                out_filepath=MyAPI.hla_melted_data_filepath,
                user_col_name="user", feature_col_name="feature", value_col_name="value")
