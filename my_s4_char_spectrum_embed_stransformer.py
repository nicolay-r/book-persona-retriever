from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from core.spectrums.presets import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from utils import CACHE_DIR
from utils_fcp import FcpApi
from utils_my import MyAPI

preset = MyAPI.spectrum_preset
model = SentenceTransformer(MyAPI.spectrum_embedding_model_name, cache_folder=CACHE_DIR)

X_norm = NpzUtils.load(MyAPI.spectrum_features_norm)
X_diff = NpzUtils.load(MyAPI.spectrum_features_diff)
prompts = PROMPT_PRESETS[preset](X_norm, X_diff, FcpApi())

X_st = []
for prompt in tqdm(prompts, desc="Calculate sentence embedding [{m}-{p}]".format(
        m=MyAPI.spectrum_embedding_model_name, p=preset)):
    X_st.append(model.encode(prompt))

# Save the result.
NpzUtils.save(X_st, MyAPI.spectrum_st_embeddings.format(preset=preset))
