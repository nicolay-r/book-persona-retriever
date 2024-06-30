from api.ldc import LdcAPI
from core.database.dialogs import DialogDatabaseWithEmbeddedTargetsHandler
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import CACHE_DIR


def handle_responses(dialog_it, handle_func):
    assert(callable(handle_func))
    for dialog_id, dialog in enumerate(dialog_it):
        speaker_q_id, query = dialog[0]
        speaker_t_id, target = dialog[1]
        handle_func(dialog_id, speaker_q_id, speaker_t_id, query, target)


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig()
    for fold in LdcAPI.dataset_folding_fixed_parts.keys():

        if fold is None:
            source = LdcAPI.dataset_filepath
            target = LdcAPI.dataset_dialog_db_path
        else:
            source = LdcAPI.dataset_fold_filepath.format(fold_index=fold)
            target = LdcAPI.dataset_dialog_db_fold_path.format(fold_index=fold)

        dialog_db = DialogDatabaseWithEmbeddedTargetsHandler(
            model_name=spectrum_cfg.embedding_model_name,
            cache_dir=CACHE_DIR,
            storage_filepath=target)

        dialog_it = LdcAPI.iter_dataset_as_dialogs(
            dataset_lines_iter=LdcAPI.read_dataset(
                source, keep_usep=False, split_meta=True,
                desc="Compose ParlAI dataset for `{}` fold part".format(fold),
                pbar=True)
        )

        with dialog_db:
            handle_responses(handle_func=dialog_db.handler,
                             dialog_it=dialog_it)
