from sentence_transformers import SentenceTransformer

from core.utils_dataset import filter_query, filter_responses
from core.utils_npz import NpzUtils
from utils import CACHE_DIR
from utils_my import MyAPI


model_name = 'all-mpnet-base-v2'
model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)

X_st = []
for u in filter_query(MyAPI.read_dataset(dataset_filepath=MyAPI.dataset_filepath)):
    X_st.append(model.encode(u))
NpzUtils.save(X_st, MyAPI.dataset_st_embedding_query)

X_st = []
for u in filter_responses(MyAPI.read_dataset(dataset_filepath=MyAPI.dataset_filepath)):
    X_st.append(model.encode(u))
NpzUtils.save(X_st, MyAPI.dataset_st_embedding_response)
