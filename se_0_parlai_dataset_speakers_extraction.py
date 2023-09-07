import random
from os import mkdir
from os.path import dirname, exists

import zipstream

from core.candidates.base import CandidatesProvider
from core.candidates.other_speakers import OtherSpeakersProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_fmt_parlai_facebook import format_episode
from utils_ceb import CEBApi
from utils_se import SEApi


def iter_formatted_dialog(dialogs_iter, traits_func, candidates_provider, candidates_oversample_factor=None):
    assert(callable(traits_func))
    assert(isinstance(candidates_provider, CandidatesProvider) or candidates_provider is None)
    assert((isinstance(candidates_oversample_factor, int) and candidates_oversample_factor > 0) or
           candidates_oversample_factor is None)

    candidates_oversample_factor = 1 \
        if candidates_oversample_factor is None or candidates_provider is None \
        else candidates_oversample_factor

    # We would like to shuffle the traits to prevent models from overfitting with the particular order.
    resp_persona_random = random.Random(SEApi.parlai_dataset_ovesampling_candidates_selection_seed)
    for dialog_id, dialog in enumerate(dialogs_iter):
        assert(len(dialog) == 2)

        r_speaker_id, query = dialog[1]
        label = candidates_provider.get_label(r_speaker_id)

        # We basically generate every episode with new candidates.
        candidates_random = random.Random(SEApi.parlai_dataset_ovesampling_candidates_selection_seed)
        for _ in range(candidates_oversample_factor):

            candidates = None

            if candidates_provider is not None:

                other_candidates = candidates_provider.provide_or_none(
                    dialog_id=dialog_id, speaker_id=r_speaker_id, label=None, random=candidates_random)
                other_candidates = [] if other_candidates is None else other_candidates
                candidates = other_candidates + [label]

                assert(len(candidates) == SEApi.parlai_dataset_candidates_limit)

                if candidates is None:
                    continue

            resp_persona_traits = traits_func(None, r_speaker_id)
            resp_persona_traits_shuffled = resp_persona_random.sample(
                resp_persona_traits, len(resp_persona_traits)) if resp_persona_traits is not None else None

            yield format_episode(request=query,
                                 response=label,
                                 candidates=candidates,
                                 resp_persona_traits=resp_persona_traits_shuffled,
                                 resp_persona_prefix=SEApi.parlai_dataset_persona_prefix,
                                 seed=SEApi.parlai_dataset_episode_candidates_and_traits_shuffle_seed).encode()
            yield b"\n"


se_api = SEApi()
z = zipstream.ZipFile()

dataset_filepaths = {part_name: se_api.dataset_fold_filepath.format(fold_index=part_name)
                     for part_name in SEApi.dataset_folding_fixed_parts}

ceb_api = CEBApi()
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

            data_it = iter_formatted_dialog(
                dialogs_iter=common_iter_dialogs(data_fold_source),
                traits_func=traits_func,
                candidates_provider=candidate_dict_func(data_fold_type),
                candidates_oversample_factor=oversample_factor)

            z = zipstream.ZipFile()

            filename = '{}.txt'.format("_".join(args))
            z.write_iter(filename, data_it)
            target = se_api.parlai_dataset_filepath.format(filename)

            if not exists(dirname(target)):
                mkdir(dirname(target))

            with open(se_api.parlai_dataset_filepath.format(filename), "wb") as f:
                for episode_line in z:
                    f.write(episode_line)

            print("Saved: {}".format(target))
