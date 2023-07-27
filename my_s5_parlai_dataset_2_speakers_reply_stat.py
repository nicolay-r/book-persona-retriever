from collections import Counter
from utils_my import MyAPI


def __count(data_type, filter_func):

    lines_it = MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=data_type),
        split_meta=True,
        desc="Read `{}` dataset".format(data_type))

    counter = Counter()
    for dialog in MyAPI.iter_dataset_as_dialogs(lines_it):
        speaker_id, utterance = filter_func(dialog)
        counter[speaker_id] += 1

    return counter


filters = {
    "resp": lambda dialog: dialog[1]
}


for f_type, f_func in filters.items():
    for data_type in ["train", "valid"]:
        c = __count(data_type, f_func)
        print(c)
