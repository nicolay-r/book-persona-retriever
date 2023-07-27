import zipstream

from core.candidates.base import CandidatesProvider
from core.candidates.clustering import ALOHANegBasedClusteringProvider
from core.candidates.default import SameBookRandomCandidatesProvider
from core.utils_parlai_facebook_formatter import format_episode
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_formatted_dialog(dialogs_iter, traits_func, candidates_provider, candidates_limit):
    assert(callable(traits_func))
    assert(isinstance(candidates_provider, CandidatesProvider) or candidates_provider is None)
    assert(isinstance(candidates_limit, int))

    for dialog_id, dialog in enumerate(dialogs_iter):
        assert(len(dialog) == 2)

        q_speaker_id, query = dialog[0]
        r_speaker_id, label = dialog[1]

        if candidates_provider is not None:
            candidates = candidates_provider.provide_or_none(
                dialog_id=dialog_id, speaker_id=r_speaker_id, label=label)
        else:
            candidates = [label]

        if candidates is None:
            continue

        yield format_episode(request=query,
                             response=label,
                             candidates=candidates,
                             resp_persona_traits=traits_func(q_speaker_id, r_speaker_id),
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

TRAITS_NO = "original"
TRAITS_SPECTRUM = "spectrum"
traits_provider = {
    TRAITS_NO: lambda your_id, partner_id: ["none"] * MyAPI.traits_per_character,
    # NOTE: In some cases (less than ~0.07%) speakers might be missed so we need to perform check.
    TRAITS_SPECTRUM: lambda your_id, partner_id: speaker_spectrums[partner_id] if partner_id in speaker_spectrums
        else traits_provider[TRAITS_NO](your_id, partner_id)
}

CANDIDATES_UTTERANCE_ONLY = ""
CANDIDATES_HLA_CLUSTER = "clustered"
candidates_provider = {

    #"_no-cands": None,

    CANDIDATES_UTTERANCE_ONLY: SameBookRandomCandidatesProvider(
        iter_dialogs=MyAPI.iter_dataset_as_dialogs(
            MyAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=MyAPI.dataset_filepath)
        ),
        candidates_per_book=1000,
        candidates_limit=MyAPI.dataset_candidates_limit),

    CANDIDATES_HLA_CLUSTER: ALOHANegBasedClusteringProvider(
        candidates_limit=MyAPI.dataset_candidates_limit,
        neg_speakers_limit=MyAPI.neg_set_speakers_limit,
        dataset_filepath=MyAPI.dataset_filepath,
        cluster_filepath=MyAPI.speaker_clusters_path,
        sqlite_dialog_db=MyAPI.dataset_dialog_db_fold_path.format("train"))
}

for data_fold_type, data_fold_source in dataset_filepaths.items():
    for trait_type, traits_func in traits_provider.items():
        for candidates_type, candidates_dict in candidates_provider.items():

            if trait_type == TRAITS_NO and candidates_type == CANDIDATES_HLA_CLUSTER:
                # This type does not makes sense, so we skip such formatting.
                continue
            if trait_type == TRAITS_SPECTRUM and candidates_type == CANDIDATES_UTTERANCE_ONLY:
                continue
            if candidates_type == CANDIDATES_HLA_CLUSTER and data_fold_type != "train":
                # We consider HLA clustering and candidates selection only for training.
                continue

            filename = '{}.txt'.format("_".join([data_fold_type, trait_type, candidates_type]))

            data_it = iter_formatted_dialog(
                dialogs_iter=MyAPI.iter_dataset_as_dialogs(
                    MyAPI.read_dataset(
                        keep_usep=False, split_meta=True, dataset_filepath=data_fold_source,
                        desc=filename)),
                traits_func=traits_func,
                candidates_provider=candidates_dict,
                candidates_limit=MyAPI.dataset_candidates_limit)

            z = zipstream.ZipFile()
            z.write_iter(filename, data_it)

            with open(my_api.dataset_parlai_filepath.format(filename), "wb") as f:
                for episode_line in z:
                    f.write(episode_line)
