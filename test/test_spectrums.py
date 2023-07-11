from core.utils_npz import NpzUtils
from utils_my import MyAPI

xn = list(NpzUtils.load(MyAPI.spectrum_features_norm))
xc = list(NpzUtils.load(MyAPI.spectrum_features_count))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))
print(xn)
print(xc)
print(y)
