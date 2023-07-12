from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from core.spectrums_emb import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils import CACHE_DIR
from utils_fcp import FcpApi
from utils_my import MyAPI

model_name = 'all-mpnet-base-v2'
preset = MyAPI.spectrum_default_preset
model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)

X_norm = list(NpzUtils.load(MyAPI.spectrum_features_norm))
X_diff = list(NpzUtils.load(MyAPI.spectrum_features_diff))
prompts = PROMPT_PRESETS[preset](X_norm, X_diff, FcpApi())

X_st = []
for prompt in tqdm(prompts, desc="Calculate sentence embedding [{m}-{p}]".format(m=model_name, p=preset)):
    X_st.append(model.encode(prompt))

# Save the result.
NpzUtils.save(X_st, MyAPI.spectrum_st_embeddings.format(preset=preset))
