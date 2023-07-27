from sentence_transformers import SentenceTransformer
from core.database.sqlite3_api import NpArraySupportDatabaseTable


class DialogDatabaseWithEmbeddedTargetsHandler(object):

    def __init__(self, model_name, cache_dir, storage_filepath=None):
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
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
