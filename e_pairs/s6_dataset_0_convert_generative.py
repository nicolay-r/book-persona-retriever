from os.path import join

import numpy as np
import zipstream

from api.ceb import CEBApi
from api.my import MyAPI
from core.dataset.pairs_iterator import common_iter_dialogs
from core.dataset.pairs_with_candidates import provide_formatted_pairs
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_math import random_choice_non_repetitive
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR


if __name__ == '__main__':

    my_api = MyAPI()
    z = zipstream.ZipFile()

    dataset_filepaths = {part_name: my_api.dataset_fold_filepath.format(fold_index=part_name)
                         for part_name in MyAPI.dataset_folding_fixed_parts}

    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    ceb_api.read_char_map()
    hla_cfg = HlaExperimentConfig(books_storage=MyAPI.books_storage)
    speaker_spectrums = SpectrumIOUtils.read(hla_cfg.hla_prompts_filepath)
    spectrum_cfg = SpectrumConfig()

    TRAITS_NO = "original"
    TRAITS_SPECTRUM = "spectrum"
    traits_provider = {
        TRAITS_NO: lambda your_id, partner_id: [None] * spectrum_cfg.spectrum_per_user_count,
        TRAITS_SPECTRUM: lambda your_id, partner_id:
        random_choice_non_repetitive(v=speaker_spectrums[partner_id]["prompts"],
                                     size=spectrum_cfg.spectrum_per_user_count,
                                     p=np.absolute(speaker_spectrums[partner_id]["weights"]),
                                     to_list=True, take_less=True)
        if partner_id in speaker_spectrums else traits_provider[TRAITS_NO](your_id, partner_id)
    }

    CANDIDATES_UNIFORM = ""
    CANDIDATES_HLA_CLUSTER = "clustered"
    candidates_provider = {
        "no-cand": lambda _: None,
    }

    for data_fold_type, data_fold_source in dataset_filepaths.items():
        for trait_type, traits_func in traits_provider.items():
            for candidates_type, candidate_dict_func in candidates_provider.items():

                if trait_type == TRAITS_NO and candidates_type == CANDIDATES_HLA_CLUSTER:
                    # This type does not makes sense, so we skip such formatting.
                    continue
                if trait_type == TRAITS_SPECTRUM and candidates_type == CANDIDATES_UNIFORM and data_fold_type == "train":
                    continue
                if candidates_type == CANDIDATES_HLA_CLUSTER and data_fold_type != "train":
                    # We consider HLA clustering and candidates selection only for training.
                    continue

                args = [data_fold_type, trait_type]
                if candidates_type != "":
                    args.append(candidates_type)

                # There is no need to perform oversampling for non-train dataset type.
                oversample_factor = None if data_fold_type != "train" else \
                    my_api.parlai_dataset_train_candidates_oversample_factor

                data_it = provide_formatted_pairs(
                    dialogs_iter=common_iter_dialogs(data_fold_source),
                    traits_func=traits_func,
                    candidates_provider=candidate_dict_func(data_fold_type),
                    candidates_oversample_factor=oversample_factor)

                z = zipstream.ZipFile()

                filename = '{}.txt'.format("_".join(args))
                z.write_iter(filename, data_it)
                target = my_api.parlai_dataset_filepath.format(filename)
                with open(my_api.parlai_dataset_filepath.format(filename), "wb") as f:
                    for episode_line in z:
                        f.write(episode_line)

                print("Saved: {}".format(target))
