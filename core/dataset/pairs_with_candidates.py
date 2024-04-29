import random

# TODO. The code should not depend on API.
from api.my import MyAPI
from api.se import SEApi

from core.candidates.base import CandidatesProvider
from core.dataset.formatters.parlai_facebook import format_episode


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
    candidates_random = random.Random(MyAPI.parlai_dataset_ovesampling_candidates_selection_seed)
    for dialog_id, dialog in enumerate(dialogs_iter):
        assert(len(dialog) == 2)

        q_speaker_id, query = dialog[0]
        r_speaker_id, label = dialog[1]

        # We basically generate every episode with new candidates.
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
                                 candidates_random=candidates_random).encode()
            yield b"\n"


def provide_formatter_pairs_speaker_extraction(dialogs_iter, ignored_speakers, traits_func,
                                               candidates_provider, candidates_oversample_factor=None):
    """ This is a quick replica of code for Speaker Extraction.
        In general, it is expected to be the same code as in method above,
        but due to the limit of time, we decided to make it a separate replica.
        Some parts of code were modified to meet the speaker extraction task.
    """
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

        if r_speaker_id in ignored_speakers:
            continue

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
                                 candidates_random=candidates_random).encode()
            yield b"\n"
