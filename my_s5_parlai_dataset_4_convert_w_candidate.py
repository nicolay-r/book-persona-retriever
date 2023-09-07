import random

import numpy as np
import zipstream

from core.candidates.base import CandidatesProvider
from core.candidates.clustering import ALOHANegBasedClusteringProvider
from core.candidates.uniform_collection import UniformCandidatesProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_fmt_parlai_facebook import format_episode
from core.utils_math import random_choice_non_repetitive
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_formatted_dialog(dialogs_iter, traits_func, candidates_provider, candidates_oversample_factor=None):
    assert(callable(traits_func))
    assert(isinstance(candidates_provider, CandidatesProvider) or candidates_provider is None)
    assert((isinstance(candidates_oversample_factor, int) and candidates_oversample_factor > 0) or
           candidates_oversample_factor is None)

    candidates_oversample_factor = 1 \
        if candidates_oversample_factor is None or candidates_provider is None \
        else candidates_oversample_factor

    # We would like to shuffle the traits to prevent models from overfitting with the particular order.
    resp_persona_random = random.Random(MyAPI.parlai_dataset_ovesampling_candidates_selection_seed)
    for dialog_id, dialog in enumerate(dialogs_iter):
        assert(len(dialog) == 2)

        q_speaker_id, query = dialog[0]
        r_speaker_id, label = dialog[1]

        # We basically generate every episode with new candidates.
        candidates_random = random.Random(MyAPI.parlai_dataset_ovesampling_candidates_selection_seed)
        for _ in range(candidates_oversample_factor):

            candidates = None

            if candidates_provider is not None:

                other_candidates = candidates_provider.provide_or_none(
                    dialog_id=dialog_id, speaker_id=r_speaker_id, label=label, random=candidates_random)
                other_candidates = [] if other_candidates is None else other_candidates
                candidates = other_candidates + [label]

                assert(len(candidates) == MyAPI.parlai_dataset_candidates_limit)

                if candidates is None:
                    continue

            resp_persona_traits = traits_func(q_speaker_id, r_speaker_id)
            resp_persona_traits_shuffled = resp_persona_random.sample(
                resp_persona_traits, len(resp_persona_traits)) if resp_persona_traits is not None else None

            yield format_episode(request=query,
                                 response=label,
                                 candidates=candidates,
                                 resp_persona_traits=resp_persona_traits_shuffled,
                                 resp_persona_prefix=MyAPI.parlai_dataset_persona_prefix,
                                 seed=MyAPI.parlai_dataset_episode_candidates_and_traits_shuffle_seed).encode()
            yield b"\n"


my_api = MyAPI()
z = zipstream.ZipFile()

dataset_filepaths = {part_name: my_api.dataset_fold_filepath.format(fold_index=part_name)
                     for part_name in MyAPI.dataset_folding_fixed_parts}

ceb_api = CEBApi()
ceb_api.read_char_map()
# roles = ceb_api.get_meta_role()
# genders = ceb_api.get_meta_gender()
speaker_spectrums = SpectrumIOUtils.read(MyAPI.hla_prompts_filepath)

TRAITS_NO = "original"
TRAITS_SPECTRUM = "spectrum"
traits_provider = {
    TRAITS_NO: lambda your_id, partner_id: [None] * MyAPI.spectrum_per_user_count,
    # NOTE: In some cases (less than ~0.07%) speakers might be missed so we need to perform check.
    TRAITS_SPECTRUM: lambda your_id, partner_id:
        random_choice_non_repetitive(v=speaker_spectrums[partner_id]["prompts"],
                                     size=my_api.spectrum_per_user_count,
                                     p=np.absolute(speaker_spectrums[partner_id]["weights"]),
                                     to_list=True, take_less=True)
        if partner_id in speaker_spectrums else traits_provider[TRAITS_NO](your_id, partner_id)
}

CANDIDATES_UNIFORM = ""
CANDIDATES_HLA_CLUSTER = "clustered"
candidates_provider = {
    CANDIDATES_UNIFORM: lambda fold_index: UniformCandidatesProvider(
        iter_dialogs=common_iter_dialogs(MyAPI.dataset_fold_filepath.format(fold_index=fold_index)),
        candidates_limit=MyAPI.parlai_dataset_candidates_limit - 1),
    CANDIDATES_HLA_CLUSTER: lambda fold_index: ALOHANegBasedClusteringProvider(
        cache_embeddings_in_memory=True,
        candidates_limit=MyAPI.parlai_dataset_candidates_limit - 1,
        neg_speakers_limit=MyAPI.hla_neg_set_speakers_limit,
        dataset_filepath=MyAPI.dataset_filepath,
        cluster_filepath=MyAPI.hla_speaker_clusters_path,
        sqlite_dialog_db=MyAPI.dataset_dialog_db_fold_path.format(fold_index=fold_index))
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

            data_it = iter_formatted_dialog(
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