from os.path import join

import zipstream

from api.ceb import CEBApi
from api.se import SEApi
from core.candidates.other_speakers import OtherSpeakersProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.dataset.pairs_with_candidates import provide_formatter_pairs_speaker_extraction
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_npz import save_zip_stream
from utils import DATA_DIR


if __name__ == '__main__':

    se_api = SEApi()
    z = zipstream.ZipFile()

    dataset_filepaths = {part_name: se_api.dataset_fold_filepath.format(fold_index=part_name)
                         for part_name in SEApi.dataset_folding_fixed_parts}

    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    ceb_api.read_char_map()
    speaker_spectrums = SpectrumIOUtils.read(SEApi.hla_prompts_filepath)

    traits_provider = {
        "": lambda your_id, partner_id: None
    }

    candidates_provider = {
        "hla-cand": lambda fold_index: OtherSpeakersProvider(
            speaker_ids=list(speaker_spectrums.keys()),
            candidates_limit=SEApi.parlai_dataset_candidates_limit - 1,
            # The way we form the result output labels.
            get_trait_func=lambda speaker_id: ",".join(speaker_spectrums[speaker_id]["prompts"])),
    }

    for data_fold_type, data_fold_source in dataset_filepaths.items():
        for trait_type, traits_func in traits_provider.items():
            for candidates_type, candidate_dict_func in candidates_provider.items():

                args = [data_fold_type, trait_type]
                if candidates_type != "":
                    args.append(candidates_type)

                # There is no need to perform oversampling for non-train dataset type.
                oversample_factor = None if data_fold_type != "train" else \
                    se_api.parlai_dataset_train_candidates_oversample_factor

                data_it = provide_formatter_pairs_speaker_extraction(
                    dialogs_iter=common_iter_dialogs(data_fold_source),
                    traits_func=traits_func,
                    candidates_provider=candidate_dict_func(data_fold_type),
                    candidates_oversample_factor=oversample_factor,
                    ignored_speakers=SEApi.ignored_speakers)

                filename = '{}.txt'.format("_".join(args))
                save_zip_stream(target=se_api.parlai_dataset_filepath.format(filename),
                                inner_filename=filename,
                                data_it=data_it)
