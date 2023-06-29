from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from core.spectrums_emb import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI

model_name = 'all-mpnet-base-v2'
preset = MyAPI.spectrum_default_preset
model = SentenceTransformer(model_name, cache_folder="./.cache")

X = list(NpzUtils.load(MyAPI.spectrum_features))
prompts = PROMPT_PRESETS[preset](X, FcpApi())

X_st = []
for prompt in tqdm(prompts, desc="Calculate sentence embedding [{m}-{p}]".format(m=model_name, p=preset)):
    X_st.append(model.encode(prompt))

# Save the result.
NpzUtils.save(X_st, MyAPI.spectrum_st_embeddings.format(preset=preset))
