from os.path import join

import numpy as np
import zipstream

from api.ceb import CEBApi
from api.ldc import LdcAPI
from core.candidates.clustering import ALOHANegBasedClusteringCandidatesProvider
from core.candidates.uniform_collection import UniformCandidatesProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.dataset.pairs_with_candidates import provide_formatted_pairs
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_math import random_choice_non_repetitive
from core.utils_npz import save_zip_stream
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR


if __name__ == '__main__':

    ldc_api = LdcAPI()
    z = zipstream.ZipFile()

    dataset_filepaths = {part_name: ldc_api.dataset_fold_filepath.format(fold_index=part_name)
                         for part_name in LdcAPI.dataset_folding_fixed_parts}

    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    ceb_api.read_char_map()
    hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
    speaker_spectrums = SpectrumIOUtils.read(hla_cfg.hla_prompts_filepath)
    spectrum_cfg = SpectrumConfig()

    TRAITS_NO = "original"
    TRAITS_SPECTRUM = "spectrum"
    traits_provider = {
        TRAITS_NO: lambda your_id, partner_id: [None] * spectrum_cfg.spectrum_per_user_count,
        # NOTE: In some cases (less than ~0.07%) speakers might be missed so we need to perform check.
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
        CANDIDATES_UNIFORM: lambda fold_index: UniformCandidatesProvider(
            iter_dialogs=common_iter_dialogs(LdcAPI.dataset_fold_filepath.format(fold_index=fold_index)),
            candidates_limit=LdcAPI.parlai_dataset_candidates_limit - 1),
        CANDIDATES_HLA_CLUSTER: lambda fold_index: ALOHANegBasedClusteringCandidatesProvider(
            cache_embeddings_in_memory=True,
            candidates_limit=LdcAPI.parlai_dataset_candidates_limit - 1,
            neg_speakers_limit=hla_cfg.hla_neg_set_speakers_limit,
            dataset_filepath=LdcAPI.dataset_filepath,
            cluster_filepath=hla_cfg.hla_speaker_clusters_path,
            sqlite_dialog_db=LdcAPI.dataset_dialog_db_fold_path.format(fold_index=fold_index))
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
                    ldc_api.parlai_dataset_train_candidates_oversample_factor

                data_it = provide_formatted_pairs(
                    dialogs_iter=common_iter_dialogs(data_fold_source),
                    traits_func=traits_func,
                    candidates_provider=candidate_dict_func(data_fold_type),
                    candidates_oversample_factor=oversample_factor)

                inner_filename = '{}.txt'.format("_".join(args))
                save_zip_stream(target=ldc_api.parlai_dataset_filepath.format(inner_filename),
                                inner_filename=inner_filename,
                                data_it=data_it)
