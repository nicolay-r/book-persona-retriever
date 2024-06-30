from random import Random

from api.ldc import LdcAPI
from core.candidates.clustering import ALOHANegBasedClusteringCandidatesProvider
from e_pairs.cfg_hla import HlaExperimentConfig


hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
provider = ALOHANegBasedClusteringCandidatesProvider(
    cache_embeddings_in_memory=True,
    candidates_limit=LdcAPI.parlai_dataset_candidates_limit,
    dataset_filepath=LdcAPI.dataset_filepath,
    cluster_filepath=hla_cfg.hla_speaker_clusters_path,
    sqlite_dialog_db=LdcAPI.dataset_dialog_db_fold_path.format(fold_index="train"))

dialogs_iter = LdcAPI.iter_dataset_as_dialogs(
    LdcAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=LdcAPI.dataset_filepath, desc="Calc"))

ovesample = 5

for dialog_id, dialog in enumerate(dialogs_iter):
    assert(len(dialog) == 2)
    q_speaker_id, _ = dialog[0]
    r_speaker_id, label = dialog[1]
    rand = Random(42)
    for s in range(ovesample):
        r = provider.provide_or_none(dialog_id=dialog_id, speaker_id=r_speaker_id, label=label, random=rand)

