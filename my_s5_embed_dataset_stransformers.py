from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from core.utils_npz import NpzUtils
from utils_my import MyAPI


def filer_query_utterances(utterances_it):
    """ Filer those queries from dataset that initiate the dialogue.
    """
    for i, u in tqdm(utterances_it):
        if u is None:
            continue
        if not u.startswith("UNKN-"):
            continue
        yield u


def filter_responses(utterances_it):
    for u in tqdm(utterances_it):
        if u is None:
            continue
        if u.startswith("UNKN-"):
            continue
        yield u


my_api = MyAPI()
model_name = 'all-mpnet-base-v2'
model = SentenceTransformer(model_name)

X_st = []
for u in filer_query_utterances(my_api.read_dataset()):
    X_st.append(model.encode(u))
NpzUtils.save(X_st, MyAPI.dataset_st_embedding_query)

X_st = []
for u in filter_responses(my_api.read_dataset()):
    X_st.append(model.encode(u))
NpzUtils.save(X_st, MyAPI.dataset_st_embedding_response)
