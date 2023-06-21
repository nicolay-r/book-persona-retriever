from core.spectrums_emb import convert_to_prompts
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.spectrum_embeddings))
prompts = convert_to_prompts(X, FcpApi())
print(prompts)
