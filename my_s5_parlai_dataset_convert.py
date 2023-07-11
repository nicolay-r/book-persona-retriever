import random

import zipstream

from core.utils_parlai_facebook_formatter import create_candidates_dict, format_episode
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_dataset_lines(dataset_source, traits_func, candidates_dict, candidates_limit, desc=None):
    assert(isinstance(dataset_source, str))
    assert(callable(traits_func))
    assert(isinstance(candidates_dict, dict) or candidates_dict is None)
    assert(isinstance(candidates_limit, int))

    dialog = []
    speaker_ids = []

    read_dataset = MyAPI.read_dataset(
        keep_usep=False, split_meta=True, dataset_filepath=dataset_source, desc=desc)

    for args in read_dataset:

        if args is None:
            dialog.clear()
            continue

        speaker_id = args[0]
        speaker_ids.append(speaker_id)
        dialog.append(args[1])

        if len(dialog) < 2:
            continue

        book_id = int(speaker_id.split('_')[0])

        candidates = [dialog[1]]
        if candidates_dict is not None:
            # pick a copy of the candidates.
            related = list(iter(candidates_dict[book_id]))
            # remove already labeled candidate.
            if candidates[0] in related:
                related.remove(candidates[0])
            # shuffle candidates.
            random.shuffle(related)
            # select the top of the shuffled.
            candidates.extend(related[:candidates_limit])

        yield format_episode(request=dialog[0],
                             response=dialog[1],
                             candidates=candidates,
                             resp_persona_traits=traits_func(speaker_ids[0], speaker_ids[1]),
                             seed=MyAPI.candidates_shuffle_seed).encode()
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
speaker_spectrums = my_api.read_speaker_spectrums()

traits_provider = {
    "original": lambda your_id, partner_id: ["none"] * MyAPI.traits_per_character,
    "spectrums": lambda your_id, partner_id: speaker_spectrums[partner_id]
}

candidates_provider = {
    #"_no-cands": None,
    "": create_candidates_dict(dataset_filepath=my_api.dataset_filepath, limit_per_book=1000),
}

for data_fold_type, data_fold_source in dataset_filepaths.items():
    for trait_type, traits_func in traits_provider.items():
        for candidates_type, candidates_dict in candidates_provider.items():
            filename = '{}_{}{}.txt'.format(data_fold_type, trait_type, candidates_type)

            data_it = iter_dataset_lines(
                dataset_source=data_fold_source,
                traits_func=traits_func,
                candidates_dict=candidates_dict,
                candidates_limit=MyAPI.dataset_candidates_limit,
                desc=filename)

            z = zipstream.ZipFile()
            z.write_iter(filename, data_it)

            with open(my_api.dataset_parlai_filepath.format(filename), "wb") as f:
                for episode_line in z:
                    f.write(episode_line)
