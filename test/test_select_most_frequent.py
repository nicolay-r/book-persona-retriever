from api.my import MyAPI
from core.spectrums.to_prompts import filter_most_distictive
from core.utils_npz import NpzUtils
from e_pairs.cfg_spectrum import SpectrumConfig


spectrum_cfg = SpectrumConfig()
X_norm = NpzUtils.load(spectrum_cfg.features_norm)
X_diff = NpzUtils.load(spectrum_cfg.features_diff)

distinctive = filter_most_distictive(X_norm, limit=20)
print(X_norm[:, distinctive].shape)
