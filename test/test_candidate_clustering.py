from tqdm import tqdm

from core.candidates.clustering import ALOHANegBasedClusteringProvider
from utils_my import MyAPI


provider = ALOHANegBasedClusteringProvider(
    cache_embeddings_in_memory=True,
    candidates_limit=MyAPI.dataset_candidates_limit,
    dataset_filepath=MyAPI.dataset_filepath,
    cluster_filepath=MyAPI.speaker_clusters_path,
    embedding_model_name=MyAPI.utterance_embedding_model_name,
    vectorized_utterances_filepath=MyAPI.dataset_responses_data_path)

for i in tqdm(range(10000)):
    r = provider.provide_or_none(speaker_id="55122_0", label="Don't want to talk")
