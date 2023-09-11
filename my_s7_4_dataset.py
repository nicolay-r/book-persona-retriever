import random

from core.candidates.base import CandidatesProvider
from core.candidates.uniform_collection import UniformCandidatesProvider
from core.dataset.pairs_iterator import common_iter_dialogs
from core.utils_fmt_parlai_facebook import format_episode
from core.utils_npz import save_zip_stream
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


for speaker_id in MyAPI.predefined_speakers:

    # Part #1 composing dataset.
    it = MyAPI.iter_dialog_question_response_pairs(
        dialogs_filapath=MyAPI.dialogs_filepath,
        dialogue_filter_func=None,
        desc="Iter dialogues for speaker `{}`".format(speaker_id))
    speaker_id_dialogs_path = speaker_id + ".dataset.txt"
    MyAPI.write_dataset(dialog_qr_pairs_iter=it,
                        filepath=speaker_id_dialogs_path,
                        speakers_set=set([speaker_id]))

    # We consider uniform candidates provider
    candidates_provider = UniformCandidatesProvider(
        # We consider other speakers from valid.
        iter_dialogs=common_iter_dialogs(MyAPI.dataset_fold_filepath.format(fold_index="valid")),
        candidates_limit=MyAPI.parlai_dataset_candidates_limit - 1)

    # ParlAI.
    data_it = iter_formatted_dialog(
        dialogs_iter=common_iter_dialogs(dialogs_dataset_filepath=speaker_id_dialogs_path),
        # No traits (temporary).
        traits_func=lambda your_id, partner_id: [None] * MyAPI.spectrum_per_user_count,
        candidates_provider=candidates_provider,
        candidates_oversample_factor=None)

    save_zip_stream(target=speaker_id + ".parlai_dataset.txt.zip",
                    inner_filename='{}.txt'.format(speaker_id + ".parlai_dataset.txt"),
                    data_it=data_it)
