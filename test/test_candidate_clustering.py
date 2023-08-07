from random import Random

from core.candidates.clustering import ALOHANegBasedClusteringProvider
from utils_my import MyAPI


provider = ALOHANegBasedClusteringProvider(
    cache_embeddings_in_memory=True,
    candidates_limit=MyAPI.parlai_dataset_candidates_limit,
    dataset_filepath=MyAPI.dataset_filepath,
    cluster_filepath=MyAPI.hla_speaker_clusters_path,
    sqlite_dialog_db=MyAPI.dataset_dialog_db_fold_path.format(fold_index="train"))

dialogs_iter = MyAPI.iter_dataset_as_dialogs(
    MyAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=MyAPI.dataset_filepath, desc="Calc"))

ovesample = 5

for dialog_id, dialog in enumerate(dialogs_iter):
    assert(len(dialog) == 2)
    q_speaker_id, _ = dialog[0]
    r_speaker_id, label = dialog[1]
    rand = Random(42)
    for s in range(ovesample):
        r = provider.provide_or_none(dialog_id=dialog_id, speaker_id=r_speaker_id, label=label, random=rand)

