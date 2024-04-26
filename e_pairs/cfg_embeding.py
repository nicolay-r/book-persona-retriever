from e_pairs.embeddings.aloha.cfg import MatrixTrainingConfig, ClusterConfig


class PairsExperimentEmbeddingConfig:

    hla_training_config = MatrixTrainingConfig(top_n=100, regularization=100, iterations=500, factor=36,
                                               conf_scale=20, random_state=649128, safe_pass=0.2)
    hla_cluster_config = ClusterConfig(perc_cutoff=10, level2_limit=30, acceptable_overlap=10, weighted=False)
