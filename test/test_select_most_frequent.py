from core.spectrums.to_prompts import filter_most_distictive
from core.utils_npz import NpzUtils
from utils_my import MyAPI


X_norm = NpzUtils.load(MyAPI.spectrum_features_norm)
X_diff = NpzUtils.load(MyAPI.spectrum_features_diff)

distinctive = filter_most_distictive(X_norm, limit=20)
print(X_norm[:, distinctive].shape)
