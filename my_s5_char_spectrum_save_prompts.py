from tqdm import tqdm

from core.spectrums_emb import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI


X = list(NpzUtils.load(MyAPI.spectrum_features))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))
prompts = PROMPT_PRESETS[MyAPI.spectrum_default_preset](X, FcpApi())

for i, speaker_prompts in tqdm(enumerate(prompts)):
    print(y[i], ":", ",".join(speaker_prompts.split(' ')))
