from collections import Counter
from os.path import join

from core.plot import draw_hist_plot
from core.utils_dataset import filter_responses, filter_query
from utils_my import MyAPI


def __count(data_type, filter_func):
    r_it = filter_func(MyAPI.read_dataset(
        dataset_filepath=MyAPI.dataset_fold_filepath.format(fold_index=data_type),
        desc="Read `{}` dataset".format(data_type)))

    counter = Counter()
    for u in r_it:
        meta = MyAPI._get_meta(u)
        u = u[len(meta):].strip()
        words_count = len(u.split(' '))
        counter[words_count] += 1

    return counter


filters = {
    "resp": lambda it: filter_responses(it),
    "query": lambda it: filter_query(it)
}

for f_type, f_func in filters.items():
    for data_type in ["train", "valid"]:
        c = __count(data_type, filter_func=f_func)
        png_path = join(MyAPI.books_storage, "dataset_{}_p{}_t{}.png".format(f_type, data_type, sum(c)))
        draw_hist_plot(c, desc="Histogram of sentence lengths in words (`{}` dataset)".format(data_type),
                       min_val=0, n_bins=25, max_val=1000,
                       save_png_path=png_path, show=False,
                       asp_hor=12, asp_ver=2, show_legend=True)
