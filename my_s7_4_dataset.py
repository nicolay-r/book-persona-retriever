from os.path import join

from core.candidates.uniform_collection import UniformCandidatesProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.dataset.pairs_with_candidates import provide_formatted_pairs
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_npz import save_zip_stream
from utils_my import MyAPI


speaker_spectrums = SpectrumIOUtils.read(join(MyAPI.selected_output_dir, "hla.txt"))

for speaker_id in MyAPI.predefined_speakers:

    # Part #1 composing dataset.
    pairs_it = MyAPI.iter_dialog_question_response_pairs(
        dialogs_filepath=MyAPI.dialogs_filepath,
        dialogue_filter_func=None,
        desc="Iter dialogues for speaker `{}`".format(speaker_id))
    speaker_id_dialogs_path = join(MyAPI.selected_output_dir, f"{speaker_id}.dataset.txt")
    MyAPI.write_dataset(dialog_qr_pairs_iter=pairs_it,
                        filepath=speaker_id_dialogs_path,
                        speakers_set={speaker_id})

    # We consider uniform candidates provider.
    candidates_provider = UniformCandidatesProvider(
        # We consider other speakers from valid.
        iter_dialogs=common_iter_dialogs(MyAPI.dataset_fold_filepath.format(fold_index="valid")),
        candidates_limit=MyAPI.parlai_dataset_candidates_limit - 1)

    # ParlAI.
    data_it = provide_formatted_pairs(
        dialogs_iter=common_iter_dialogs(dialogs_dataset_filepath=speaker_id_dialogs_path),
        # Human Level Attributes traits.
        traits_func=lambda your_id, partner_id: speaker_spectrums[partner_id]["prompts"],
        candidates_provider=candidates_provider,
        # No need, because it is for the `test`.
        candidates_oversample_factor=None)

    save_zip_stream(target=join(MyAPI.selected_output_dir, f"{speaker_id}.parlai_dataset.txt.zip"),
                    inner_filename=f"valid_{speaker_id}.txt",
                    data_it=data_it)
