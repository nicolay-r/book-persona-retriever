from core.spectrums_emb import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI


X = list(NpzUtils.load(MyAPI.spectrum_features))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

prompts = PROMPT_PRESETS[MyAPI.spectrum_default_preset](X, FcpApi())
my_api = MyAPI()

my_api.save_speaker_spectrums(speaker_names=y, speaker_prompts=prompts)
