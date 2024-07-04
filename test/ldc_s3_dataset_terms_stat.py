from collections import Counter
from os.path import join

from api.ldc import LdcAPI
from core.dataset.pairs_iterator import get_dialog_qr_pairs_iter
from core.plot import draw_hist_plot
from core.utils_counter import CounterService
from utils import TEST_DIR


def calc_words_count(fold_index, filter_func):

    filepath = LdcAPI.dataset_fold_filepath.format(fold_index=fold_index) \
        if fold_index is not None else LdcAPI.dataset_filepath

    words_count_stat = Counter()
    for _, dialog in get_dialog_qr_pairs_iter(filepath=filepath, desc="Iter dialogues"):
        utterance = filter_func(dialog)
        words_count = len(utterance.split(' '))
        words_count_stat[words_count] += 1

    return words_count_stat


if __name__ == '__main__':

    filters = {
        "query": lambda dialog: dialog[0],
        "resp": lambda dialog: dialog[1]
    }

    for f_type, f_func in filters.items():

        folding_parts = [None] + \
                        list(LdcAPI.dataset_folding_fixed_parts.keys()) + \
                        list(range(LdcAPI.dataset_folding_parts))

        for data_type in folding_parts:
            c = calc_words_count(data_type, filter_func=f_func)
            sdt = data_type if data_type is not None else "all"
            png_path = join(TEST_DIR, f"dataset_{f_type}_p{sdt}.png")
            print(f_type, sdt, c.most_common(10))
            draw_hist_plot(CounterService.to_melt_list(ctr=c),
                           desc=f"Histogram of {f_type} utterance lengths in words (`{sdt}` dataset)",
                           n_bins=20, save_png_path=png_path, show=False, asp_hor=14, asp_ver=2,
                           x_min=0, x_max=round(max(c.keys()), -1),
                           log_scale=False)
