from collections import Counter
from os.path import join

from core.dialogue.speaker_annotation import iter_speaker_annotated_dialogs
from core.plot import draw_hist_plot
from utils_my import MyAPI


my_api = MyAPI()
stat_origin = MyAPI.calc_annotated_dialogs_stat(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        book_path_func=my_api.get_book_path,
        prefix_lexicon=my_api.load_prefix_lexicon_en(),
        recognize_at_positions=my_api.dialogs_recognize_speaker_at_positions)
)

cc = Counter({k: c for k, c in stat_origin["speakers_reply_stat"].items()
              if c >= my_api.dataset_filter_speaker_min_utterances_per_speaker and
              my_api.dataset_filter_speaker_min_utterances_per_speaker is not None})

draw_hist_plot(cc, n_bins=20,
               desc="Speakers reply stat origin",
               save_png_path=join(MyAPI.books_storage, "dataset_speakers_reply_origin.png"),
               show=False, asp_hor=12, asp_ver=2,
               min_val=0, max_val=my_api.dataset_filter_dialogue_max_utterances_per_speaker)
