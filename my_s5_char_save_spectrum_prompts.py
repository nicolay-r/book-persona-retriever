from core.spectrums.presets import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI


X_norm = list(NpzUtils.load(MyAPI.spectrum_features_norm))
X_diff = list(NpzUtils.load(MyAPI.spectrum_features_diff))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

prompts = PROMPT_PRESETS[MyAPI.spectrum_default_preset](X_norm, X_diff, FcpApi())

MyAPI.save_speaker_spectrums(filepath=MyAPI.spectrum_prompts_filepath, speaker_names=y, speaker_prompts=prompts)
