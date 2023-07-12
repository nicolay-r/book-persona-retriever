from core.spectrums_emb import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI

xn = list(NpzUtils.load(MyAPI.spectrum_features_norm))
xc = list(NpzUtils.load(MyAPI.spectrum_features_diff))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))
print(xn)
print(xc)
print(y)

prompts = PROMPT_PRESETS[MyAPI.spectrum_default_preset](xn, xc, FcpApi())
