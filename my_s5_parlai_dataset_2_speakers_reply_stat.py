from collections import Counter
from core.utils_dataset import filter_responses
from utils_my import MyAPI


def __count(data_type, filter_func):
    r_it = filter_func(MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=data_type),
        desc="Read `{}` dataset".format(data_type)))

    counter = Counter()
    for u in r_it:
        speaker_name = MyAPI._get_meta(u)
        counter[speaker_name] += 1

    return counter


filters = {
    "resp": lambda it: filter_responses(it),
}


for f_type, f_func in filters.items():
    for data_type in ["train", "valid"]:
        c = __count(data_type, f_func)
        print(c)
