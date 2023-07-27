from sentence_transformers import SentenceTransformer

from core.database.sqlite3_api import NpArraySupportDatabaseTable
from utils import CACHE_DIR
from utils_my import MyAPI


class DialogDatabaseWithEmbeddedTargetsHandler(object):

    def __init__(self, model_name, storage_filepath=None):
        self.model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)
        self.storage_filepath = storage_filepath
        self.dt = NpArraySupportDatabaseTable(commit_after=10)

    def handler(self, dialog_id, speaker_q_id, speaker_t_id, query, target):
        self.dt.insert_table((
            dialog_id,
            speaker_q_id,
            speaker_t_id,
            query,
            target,
            self.model.encode(target)))

    def __enter__(self):
        self.dt.connect(self.storage_filepath)
        self.dt.create_table(
            column_with_types=[
                ("dialog_id", "integer"),
                ("speaker_q_id", "text"),
                ("speaker_t_id", "text"),
                ("query", "text"),
                ("target", "text"),
                ("target_vector", NpArraySupportDatabaseTable.ARRAY_TYPE)
            ],
            drop_if_exists=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dt.close()


def handle_responses(dialog_it, handle_func):
    assert(callable(handle_func))
    for dialog_id, dialog in enumerate(dialog_it):
        speaker_q_id, query = dialog[0]
        speaker_t_id, target = dialog[1]
        handle_func(dialog_id, speaker_q_id, speaker_t_id, query, target)


dialog_db = DialogDatabaseWithEmbeddedTargetsHandler(
    model_name=MyAPI.utterance_embedding_model_name,
    storage_filepath=MyAPI.dataset_dialog_db_path)

# Dataset dialog iterator.
dialog_it = MyAPI.iter_dataset_as_dialogs(
    dataset_lines_iter=MyAPI.read_dataset(
        MyAPI.dataset_filepath, keep_usep=False, split_meta=True, desc=None, pbar=True)
)

with dialog_db:
    handle_responses(handle_func=dialog_db.handler,
                     dialog_it=dialog_it)
