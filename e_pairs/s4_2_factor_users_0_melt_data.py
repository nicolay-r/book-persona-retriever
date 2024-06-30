from api.ldc import LdcAPI
from core.factor.utils import melt_to_csv
from core.utils_npz import NpzUtils
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig


if __name__ == '__main__':

    hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
    spectrum_cfg = SpectrumConfig()
    melt_to_csv(X=list(NpzUtils.load(spectrum_cfg.features_norm)),
                y=list(NpzUtils.load(spectrum_cfg.speakers)),
                out_filepath=hla_cfg.hla_melted_data_filepath,
                user_col_name="user", feature_col_name="feature", value_col_name="value")
