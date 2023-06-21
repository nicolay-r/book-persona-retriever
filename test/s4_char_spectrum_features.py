import numpy as np

from core.spectrums_emb import filter_by_non_zero
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.spectrum_embeddings))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

X, y = filter_by_non_zero(X=X, y=y, threshold=190)

vals_greater_0 = (np.array(X) > 0).sum()
vals_less_0 = (np.array(X) < 0).sum()

print(vals_greater_0)
print(vals_less_0)
