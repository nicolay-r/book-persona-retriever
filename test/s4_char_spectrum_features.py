import numpy as np

from core.utils_npz import NpzUtils
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.spectrum.presets import FILTER_PRESETS


spectrum_cfg = SpectrumConfig()
X = list(NpzUtils.load(spectrum_cfg.features_norm))
y = list(NpzUtils.load(spectrum_cfg.speakers))

X, y = FILTER_PRESETS["original-no-color"](X, y)

vals_greater_0 = (np.array(X) > 0).sum()
vals_less_0 = (np.array(X) < 0).sum()

print(vals_greater_0)
print(vals_less_0)
