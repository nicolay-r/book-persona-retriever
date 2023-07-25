from core.candidates.clustering import ALOHANegBasedClusteringProvider
from utils_my import MyAPI


provider = ALOHANegBasedClusteringProvider(
    limit_per_char=100,
    candidates_limit=MyAPI.dataset_candidates_limit,
    dataset_filepath=MyAPI.dataset_filepath,
    cluster_filepath=MyAPI.speaker_clusters_path)

r = provider.provide(speaker_id="55122_0", label="Don't want to talk")
