from sentence_transformers import SentenceTransformer

from core.database.sqlite3_api import NpArraySupportDatabaseTable
from utils import CACHE_DIR
from utils_my import MyAPI


def handle_responses(it, handle_func):
    assert(callable(handle_func))

    lines = []
    for args in it:

        if args is None:
            lines.clear()
            continue

        lines.append(args)

        if len(lines) < 2:
            continue

        speaker_id, utterance = args

        handle_func(speaker_id, utterance)


class SentenceTransformerBasedHandler(object):

    def __init__(self, model_name, storage_filepath=None):
        self.model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)
        self.storage_filepath = storage_filepath
        self.dt = NpArraySupportDatabaseTable(commit_after=10)

    def handler(self, speaker_id, utterance):
        self.dt.insert_table((speaker_id, utterance, self.model.encode(utterance)))

    def __enter__(self):
        self.dt.connect(self.storage_filepath)
        self.dt.create_table(
            column_with_types=[
                ("speakerid", "text"),
                ("utterance", "text"),
                ("vector", NpArraySupportDatabaseTable.ARRAY_TYPE)
            ],
            drop_if_exists=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dt.close()


my_api = MyAPI()
s_trans_handler = SentenceTransformerBasedHandler(
    model_name=MyAPI.utterance_embedding_model_name,
    storage_filepath=MyAPI.dataset_responses_data_path)
it = my_api.read_dataset(my_api.dataset_filepath, keep_usep=False,
                         split_meta=True, desc=None, pbar=True)

with s_trans_handler:
    handle_responses(handle_func=s_trans_handler.handler, it=it)
