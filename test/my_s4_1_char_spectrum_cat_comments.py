from os.path import join

from core.dialogue.comments import filter_relevant_text_comments
from core.spectrums_annot import annot_spectrums_in_text
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from test.const import MOST_DISTINCTIVE
from utils import DATA_DIR
from utils_draw import draw_spectrums_stat
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
speaker_spectrums = MyAPI.read_speakers()
print("Speakers considered: {}".format(len(speaker_spectrums)))

my_api = MyAPI()
g_api = GuttenbergDialogApi()
spectrum_cfg = SpectrumConfig(books_storage=my_api.books_storage)
speaker_spectrums = annot_spectrums_in_text(
    texts_and_speakervars_iter=filter_relevant_text_comments(
        is_term_speaker_func=GuttenbergDialogApi.is_character,
        speaker_positions=spectrum_cfg.comment_speaker_positions,
        iter_comments_at_k_func=lambda k: g_api.filter_comment_with_speaker_at_k(
            book_path_func=my_api.get_book_path, k=k),
        speakers=set(speaker_spectrums)),
    rev_spectrums=fcp_api.reversed_spectrums())


# Compose global stat.
draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                    fcp_api=fcp_api,
                    top_bars_count=20, bottom_bars_count=20,
                    save_png_filepath="spectrum-all-comments.png")

# Compose global stat.
draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                    fcp_api=fcp_api,
                    top_bars_count=20, bottom_bars_count=20,
                    spectrums_keep=MOST_DISTINCTIVE,
                    asp_ver=6, asp_hor=2,
                    save_png_filepath="spectrum-all-comments-most-distinctive.png")
