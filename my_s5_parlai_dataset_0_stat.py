from collections import Counter
from os.path import join
from core.plot import draw_hist_plot
from utils_my import MyAPI


def __count(data_type, filter_func):

    lines_it = MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=data_type),
        keep_usep=True,
        split_meta=True,
        desc="Read `{}` dataset".format(data_type))

    c = Counter()
    for dialog in MyAPI.iter_dataset_as_dialogs(lines_it):
        meta, utterance = filter_func(dialog)
        words_count = len(utterance.split(' '))
        c[words_count] += 1

    return c


filters = {
    "query": lambda dialog: dialog[0],
    "resp": lambda dialog: dialog[1]
}

for f_type, f_func in filters.items():
    for data_type in ["train", "valid"]:
        c = __count(data_type, filter_func=f_func)
        png_path = join(MyAPI.books_storage, "dataset_{}_p{}_t{}.png".format(f_type, data_type, sum(c)))
        draw_hist_plot(c, desc="Histogram of sentence lengths in words (`{}` dataset)".format(data_type),
                       n_bins=20, save_png_path=png_path, show=False, asp_hor=12, asp_ver=2, min_val=0)
