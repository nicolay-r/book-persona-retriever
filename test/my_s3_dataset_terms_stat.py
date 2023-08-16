from collections import Counter
from os.path import join
from core.dataset.pairs_iterator import get_dialog_qr_pairs_iter
from core.plot import draw_hist_plot
from utils_my import MyAPI


def calc_words_count(fold_index, filter_func):

    filepath = MyAPI.dataset_fold_filepath.format(fold_index=fold_index) \
        if fold_index is not None else MyAPI.dataset_filepath

    words_count_stat = Counter()
    for _, dialog in get_dialog_qr_pairs_iter(filepath=filepath, desc="Iter dialogues"):
        utterance = filter_func(dialog)
        words_count = len(utterance.split(' '))
        words_count_stat[words_count] += 1

    return words_count_stat


filters = {
    "query": lambda dialog: dialog[0],
    "resp": lambda dialog: dialog[1]
}

for f_type, f_func in filters.items():

    folding_parts = [None] + \
                    list(MyAPI.dataset_folding_fixed_parts.keys()) + \
                    list(range(MyAPI.dataset_folding_parts))

    for data_type in folding_parts:
        c = calc_words_count(data_type, filter_func=f_func)
        sdt = data_type if data_type is not None else "all"
        png_path = join(MyAPI.books_storage, f"dataset_{f_type}_p{sdt}.png")
        print(f_type, sdt, c.most_common(10))
        draw_hist_plot(c,
                       desc=f"Histogram of {f_type} utterance lengths in words (`{sdt}` dataset)",
                       n_bins=20, save_png_path=png_path, show=False, asp_hor=14, asp_ver=2,
                       # Round to the closest 10.
                       max_val=round(max(c.keys()), -1),
                       log_scale=False)
