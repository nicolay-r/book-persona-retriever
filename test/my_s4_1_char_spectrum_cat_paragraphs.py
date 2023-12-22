from collections import Counter
from os.path import join

from core.book.utils import iter_paragraphs_with_n_speakers
from core.plot import draw_hist_plot
from core.spectrums_annot import annot_spectrums_in_text
from test.const import MOST_DISTINCTIVE
from utils_draw import draw_spectrums_stat
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_my import MyAPI


# We connect the CEB API for our books in English,
# for which annotation of the characters has been applied.
my_api = MyAPI()
fcp_api = FcpApi()
ds_speakers = my_api.read_speakers()

speaker_spectrums = annot_spectrums_in_text(
    texts_and_speakervars_iter=map(lambda t: (t[0].Text, t[1]),
                                   iter_paragraphs_with_n_speakers(
                                       multi_mentions=False,
                                       speakers=set(ds_speakers),
                                       n_speakers=MyAPI.spectrum_speakers_in_paragraph,
                                       iter_paragraphs=CEBApi.iter_paragraphs(
                                           iter_book_ids=my_api.book_ids_from_directory(),
                                           book_by_id_func=my_api.get_book_path))),
    rev_spectrums=fcp_api.reversed_spectrums())

draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                    fcp_api=fcp_api,
                    top_bars_count=20,
                    bottom_bars_count=20,
                    save_png_filepath="spectrum-all-paragraphs.png")

most_distinctive = set()
draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                    fcp_api=fcp_api,
                    top_bars_count=20, bottom_bars_count=20,
                    spectrums_keep=MOST_DISTINCTIVE,
                    asp_ver=6, asp_hor=2,
                    save_png_filepath="spectrum-all-paragraphs-most-distinctive.png")

# Compose global stat.
s_counter = Counter()
for name, spectrum_ctr in speaker_spectrums.items():
    s_counter[name] = len(spectrum_ctr)

png_path = join(MyAPI.books_storage, f"spectrums_per_speaker.png")
draw_hist_plot(c=s_counter, save_png_path=png_path, desc='Spectrums Per Speaker',
               min_val=0, max_val=20, asp_hor=14, asp_ver=2, show=False)
