import json

from sentence_transformers import SentenceTransformer

from core.utils_npz import NpzUtils
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

    def __init__(self, model_name='all-mpnet-base-v2', y_filepath=None):
        self.model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)
        self.y_filepath = y_filepath
        self.y_file = None
        self.X = []

    def handler(self, speaker_id, utterance):
        self.X.append(self.model.encode(utterance))
        d = {"speaker_id": speaker_id, "utterance": utterance}
        self.y_file.write("{}\n".format(json.dumps(d)))

    def __enter__(self):
        self.y_file = open(self.y_filepath, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.y_file.close()


my_api = MyAPI()
s_trans_handler = SentenceTransformerBasedHandler(
    y_filepath=MyAPI.dataset_responses_data_path)
it = my_api.read_dataset(my_api.dataset_filepath, keep_usep=True,
                         split_meta=True, desc=None, pbar=True, limit=1000)

with s_trans_handler:
    handle_responses(handle_func=s_trans_handler.handler, it=it)

NpzUtils.save(data=s_trans_handler.X,
              target=MyAPI.dataset_responses_embeddings_path)
