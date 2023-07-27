from core.database.dialogs import DialogDatabaseWithEmbeddedTargetsHandler
from utils import CACHE_DIR
from utils_my import MyAPI


def handle_responses(dialog_it, handle_func):
    assert(callable(handle_func))
    for dialog_id, dialog in enumerate(dialog_it):
        speaker_q_id, query = dialog[0]
        speaker_t_id, target = dialog[1]
        handle_func(dialog_id, speaker_q_id, speaker_t_id, query, target)


for fold in [None, "train", "test"]:

    if fold is None:
        source = MyAPI.dataset_filepath
        target = MyAPI.dataset_dialog_db_path
    else:
        source = MyAPI.dataset_fold_filepath.format(fold_index=fold)
        target = MyAPI.dataset_dialog_db_fold_path.format(fold_index=fold)

    dialog_db = DialogDatabaseWithEmbeddedTargetsHandler(
        model_name=MyAPI.utterance_embedding_model_name,
        cache_dir=CACHE_DIR,
        storage_filepath=target)

    dialog_it = MyAPI.iter_dataset_as_dialogs(
        dataset_lines_iter=MyAPI.read_dataset(
            source, keep_usep=False, split_meta=True,
            desc="Compose for `{}` fold part".format(fold),
            pbar=True)
    )

    with dialog_db:
        handle_responses(handle_func=dialog_db.handler,
                         dialog_it=dialog_it)
