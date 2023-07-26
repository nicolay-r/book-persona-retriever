from core.candidates.clustering import ALOHANegBasedClusteringProvider
from utils_my import MyAPI


provider = ALOHANegBasedClusteringProvider(
    candidates_limit=MyAPI.dataset_candidates_limit,
    dataset_filepath=MyAPI.dataset_filepath,
    cluster_filepath=MyAPI.speaker_clusters_path,
    vectorized_utterances_filepath=MyAPI.dataset_responses_data_path)

r = provider.provide_or_none(speaker_id="55122_0", label="Don't want to talk")
print(r)
