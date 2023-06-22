import numpy as np

from core.spectrums_emb import FILTER_PRESETS
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.spectrum_features))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

X, y = FILTER_PRESETS["original-no-color"](X, y, None)

vals_greater_0 = (np.array(X) > 0).sum()
vals_less_0 = (np.array(X) < 0).sum()

print(vals_greater_0)
print(vals_less_0)
