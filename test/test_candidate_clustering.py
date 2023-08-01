from core.candidates.clustering import ALOHANegBasedClusteringProvider
from utils_my import MyAPI


provider = ALOHANegBasedClusteringProvider(
    cache_embeddings_in_memory=True,
    candidates_limit=MyAPI.parlai_dataset_candidates_limit,
    dataset_filepath=MyAPI.dataset_filepath,
    cluster_filepath=MyAPI.speaker_clusters_path,
    sqlite_dialog_db=MyAPI.dataset_dialog_db_path)

dialogs_iter = MyAPI.iter_dataset_as_dialogs(
    MyAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=MyAPI.dataset_filepath, desc="Calc"))

for dialog_id, dialog in enumerate(dialogs_iter):
    assert(len(dialog) == 2)
    q_speaker_id, _ = dialog[0]
    r_speaker_id, label = dialog[1]
    r = provider.provide_or_none(dialog_id=dialog_id, speaker_id=r_speaker_id, label=label)

