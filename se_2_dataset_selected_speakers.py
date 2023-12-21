from os.path import join

from core.candidates.other_speakers import OtherSpeakersProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.dataset.pairs_with_candidates import provide_formatter_pairs_speaker_extraction
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_npz import save_zip_stream
from utils_my import MyAPI
from utils_se import SEApi


speaker_spectrums = SpectrumIOUtils.read([
    # We use speaker prompts from the MyAPI dataset (for the filtered speakers, i.e. 400 in past experiments).
    MyAPI.hla_prompts_filepath,
    # In addition we consider the selected speakers to add in that list.
    join(SEApi.selected_output_dir, "hla.txt")])

for speaker_id in SEApi.predefined_speakers:

    # Part #1 composing dataset.
    pairs_it = MyAPI.iter_dialog_question_response_pairs(
        dialogs_filepath=MyAPI.dialogs_filepath,
        dialogue_filter_func=None,
        desc="Iter dialogues for speaker `{}`".format(speaker_id))

    # Speaker id dialogs output filepath.
    speaker_id_dialogs_path = join(SEApi.selected_output_dir, speaker_id + ".dataset.txt")

    MyAPI.write_dataset(dialog_qr_pairs_iter=pairs_it,
                        filepath=speaker_id_dialogs_path,
                        speakers_set={speaker_id})

    # We consider provider of other speakers.
    candidates_provider = OtherSpeakersProvider(
        speaker_ids=list(speaker_spectrums.keys()),
        candidates_limit=SEApi.parlai_dataset_candidates_limit - 1,
        # The way we form the result output labels.
        get_trait_func=lambda speaker_id: ",".join(speaker_spectrums[speaker_id]["prompts"]))

    # ParlAI.
    data_it = provide_formatter_pairs_speaker_extraction(
        dialogs_iter=common_iter_dialogs(dialogs_dataset_filepath=speaker_id_dialogs_path),
        # We do not serve with any traits about speaker.
        traits_func=lambda your_id, partner_id: None,
        candidates_provider=candidates_provider,
        # No need, because it is for the `test`.
        candidates_oversample_factor=None,
        ignored_speakers=SEApi.ignored_speakers)

    save_zip_stream(target=join(SEApi.selected_output_dir, f"{speaker_id}.parlai_dataset.txt.zip"),
                    inner_filename=f"valid_{speaker_id}.txt",
                    data_it=data_it)
