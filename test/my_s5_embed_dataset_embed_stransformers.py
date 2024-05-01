from sentence_transformers import SentenceTransformer

from api.my import MyAPI
from core.utils_npz import NpzUtils
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import CACHE_DIR


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig()
    model = SentenceTransformer(spectrum_cfg.embedding_model_name, cache_folder=CACHE_DIR)

    X_q = []
    X_r = []

    dialogs_it = MyAPI.iter_dataset_as_dialogs(
        dataset_lines_iter=MyAPI.read_dataset(
            dataset_filepath=MyAPI.dataset_filepath,
            keep_usep=False,
            split_meta=True))

    for dialog in dialogs_it:
        assert (isinstance(dialog, list) and len(dialog) == 2)
        q_meta, q_utterance = dialog[0]
        X_q.append(model.encode(q_utterance))
        r_meta, r_utterance = dialog[1]
        X_r.append(model.encode(r_utterance))

    NpzUtils.save(X_q, MyAPI.dataset_st_embedding_query)
    NpzUtils.save(X_r, MyAPI.dataset_st_embedding_response)
