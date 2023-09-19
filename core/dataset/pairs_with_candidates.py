import random
from core.candidates.base import CandidatesProvider
from core.dataset.formatters.llm import format_episode
from utils_my import MyAPI


def provide_formatted_pairs(dialogs_iter, traits_func, candidates_provider, candidates_oversample_factor=None):
    """ Provides the dataset into the specific format.
    """
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