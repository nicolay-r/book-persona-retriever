import zipstream

from core.utls_parlai_facebook_formatter import format_episode
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_dataset_lines(my_api, dataset_source, traits_func, desc=None):
    assert(callable(traits_func))

    dialog = []
    speaker_ids = []

    read_dataset = my_api.read_dataset(
        keep_usep=False, split_meta=True, dataset_filepath=dataset_source, desc=desc)

    for args in read_dataset:

        if args is None:
            dialog.clear()
            continue

        speaker_ids.append(args[0])
        dialog.append(args[1])

        if len(dialog) < 2:
            continue

        yield format_episode(request=dialog[0],
                             response=dialog[1],
                             candidates=[dialog[1]],
                             resp_persona_traits=traits_func(speaker_ids[0], speaker_ids[1])).encode()
        yield b"\n"


my_api = MyAPI()
z = zipstream.ZipFile()


dataset_filepaths = {
    "train": my_api.dataset_fold_filepath.format(fold_index="train"),
    "valid": my_api.dataset_fold_filepath.format(fold_index="valid")
}

ceb_api = CEBApi()
ceb_api.read_char_map()
speaker_spectrums = my_api.read_speaker_spectrums()

traits_provider = {
    "original": lambda your_id, partner_id:
        [ceb_api.replace_characters_in_text(partner_id)],
    "spectrums": lambda your_id, partner_id:
        # original
        traits_provider["original"](your_id, partner_id) +
        # + spectrums
        speaker_spectrums[partner_id]
}

for data_fold_type, data_fold_source in dataset_filepaths.items():
    for trait_type, traits_func in traits_provider.items():
        filename = '{}_{}.txt'.format(data_fold_type, trait_type)

        data_it = iter_dataset_lines(
            my_api=my_api,
            dataset_source=data_fold_source,
            traits_func=traits_func,
            desc=filename)

        z = zipstream.ZipFile()
        z.write_iter(filename, data_it)

        with open(my_api.dataset_parlai_filepath.format(filename), "wb") as f:
            for episode_line in z:
                f.write(episode_line)
