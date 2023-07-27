import zipstream

from core.candidates.base import CandidatesProvider
from core.candidates.clustering import ALOHANegBasedClusteringProvider
from core.candidates.default import SameBookRandomCandidatesProvider
from core.utils_parlai_facebook_formatter import format_episode
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_dataset_lines(dataset_source, traits_func, candidates_provider, candidates_limit, desc=None):
    assert(isinstance(dataset_source, str))
    assert(callable(traits_func))
    assert(isinstance(candidates_provider, CandidatesProvider) or candidates_provider is None)
    assert(isinstance(candidates_limit, int))

    dialog = []
    speaker_ids = []

    read_dataset = MyAPI.read_dataset(
        keep_usep=False, split_meta=True, dataset_filepath=dataset_source, desc=desc)

    for args in read_dataset:

        if args is None:
            dialog.clear()
            speaker_ids.clear()
            continue

        speaker_id = args[0]
        speaker_ids.append(speaker_id)
        dialog.append(args[1])

        if len(dialog) < 2:
            continue

        assert(len(dialog) == len(speaker_ids) == 2)

        label = dialog[1]
        if candidates_provider is not None:
            candidates = candidates_provider.provide_or_none(speaker_id=speaker_id, label=label)
        else:
            candidates = [label]

        if candidates is None:
            continue

        yield format_episode(request=dialog[0],
                             response=dialog[1],
                             candidates=candidates,
                             resp_persona_traits=traits_func(speaker_ids[0], speaker_ids[1]),
                             resp_persona_prefix=MyAPI.response_persona_prefix,
                             seed=MyAPI.candidates_and_traits_shuffle_seed).encode()
        yield b"\n"


my_api = MyAPI()
z = zipstream.ZipFile()


dataset_filepaths = {
    "train": my_api.dataset_fold_filepath.format(fold_index="train"),
    "valid": my_api.dataset_fold_filepath.format(fold_index="valid")
}

ceb_api = CEBApi()
ceb_api.read_char_map()
# roles = ceb_api.get_meta_role()
# genders = ceb_api.get_meta_gender()
speaker_spectrums = MyAPI.read_speaker_spectrums(MyAPI.spectrum_prompts_filepath)

traits_provider = {
    "original": lambda your_id, partner_id: ["none"] * MyAPI.traits_per_character,
    # NOTE: In some cases (less than ~0.07%) speakers might be missed so we need to perform check.
    "spectrums": lambda your_id, partner_id: speaker_spectrums[partner_id] if partner_id in speaker_spectrums
        else traits_provider["original"](your_id, partner_id)
}

candidates_provider = {
    #"_no-cands": None,
    "": SameBookRandomCandidatesProvider(candidates_per_book=1000,
                                         candidates_limit=MyAPI.dataset_candidates_limit,
                                         dataset_filepath=MyAPI.dataset_filepath),
    "clustered": ALOHANegBasedClusteringProvider(
        candidates_limit=MyAPI.dataset_candidates_limit,
        neg_speakers_limit=MyAPI.neg_set_speakers_limit,
        embedding_model_name=MyAPI.utterance_embedding_model_name,
        dataset_filepath=MyAPI.dataset_filepath,
        cluster_filepath=MyAPI.speaker_clusters_path,
        vectorized_utterances_filepath=MyAPI.dataset_responses_data_path)
}

for data_fold_type, data_fold_source in dataset_filepaths.items():
    for trait_type, traits_func in traits_provider.items():
        for candidates_type, candidates_dict in candidates_provider.items():
            filename = '{}_{}{}.txt'.format(data_fold_type, trait_type, candidates_type)

            data_it = iter_dataset_lines(
                dataset_source=data_fold_source,
                traits_func=traits_func,
                candidates_provider=candidates_dict,
                candidates_limit=MyAPI.dataset_candidates_limit,
                desc=filename)

            z = zipstream.ZipFile()
            z.write_iter(filename, data_it)

            with open(my_api.dataset_parlai_filepath.format(filename), "wb") as f:
                for episode_line in z:
                    f.write(episode_line)
