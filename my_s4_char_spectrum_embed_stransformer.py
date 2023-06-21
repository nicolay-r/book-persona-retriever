from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from core.spectrums_emb import convert_to_prompts
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI

model_name = 'all-mpnet-base-v2'
model = SentenceTransformer(model_name)

X = list(NpzUtils.load(MyAPI.spectrum_embeddings))
prompts = convert_to_prompts(X, FcpApi())

X_st = []
for prompt in tqdm(prompts, desc="Calculate sentence embedding [{}]".format(model_name)):
    X_st.append(model.encode(prompt))

# Save the result.
NpzUtils.save(X_st, MyAPI.spectrum_st_embeddings)
