from collections import Counter
from os.path import join

from api.ceb import CEBApi
from api.gd import GuttenbergDialogApi
from api.ldc import LdcAPI
from core.book.utils import iter_paragraphs_with_n_speakers
from core.plot import draw_hist_plot
from core.utils import create_dir_if_not_exist
from core.utils_counter import CounterService
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.hla_models.spectrum.annot import annot_spectrums_in_text
from test.const import MOST_DISTINCTIVE
from utils import DATA_DIR, TEST_DIR
from utils_draw import draw_spectrums_stat


if __name__ == '__main__':

    # We connect the CEB API for our books in English,
    # for which annotation of the characters has been applied.
    ldc_api = LdcAPI()
    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    ds_speakers = ldc_api.read_speakers()
    spectrum_cfg = SpectrumConfig()

    speaker_spectrums = annot_spectrums_in_text(
        texts_and_speakervars_iter=map(lambda t: (t[0].Text, t[1]),
                                       iter_paragraphs_with_n_speakers(
                                           multi_mentions=False,
                                           speakers=set(ds_speakers),
                                           n_speakers=spectrum_cfg.speakers_in_paragraph,
                                           cast_to_id_or_none=lambda term:
                                               CEBApi.speaker_variant_to_speaker(
                                                   GuttenbergDialogApi.try_parse_character(term, default=""),
                                                   return_none=True),
                                           paragraph_to_terms=lambda p: CEBApi.separate_character_entries(p.Text).split(),
                                           cast_to_variant_or_none=lambda term:
                                               GuttenbergDialogApi.try_parse_character(term, default=None),
                                           iter_paragraphs=CEBApi.iter_paragraphs(
                                               iter_book_ids=ldc_api.book_ids_from_directory(),
                                               book_by_id_func=ldc_api.get_book_path))),
        rev_spectrums=fcp_api.reversed_spectrums())

    # Create test directory.
    create_dir_if_not_exist(TEST_DIR)

    draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                        fcp_api=fcp_api,
                        top_bars_count=20,
                        bottom_bars_count=20,
                        save_png_filepath=join(TEST_DIR, "spectrum-all-paragraphs.png"))

    create_dir_if_not_exist(TEST_DIR)
    draw_spectrums_stat(speaker_spectrum_counters=speaker_spectrums.values(),
                        fcp_api=fcp_api,
                        top_bars_count=20, bottom_bars_count=20,
                        spectrums_keep=MOST_DISTINCTIVE,
                        asp_ver=6, asp_hor=2,
                        save_png_filepath=join(TEST_DIR, "spectrum-all-paragraphs-most-distinctive.png"))

    # Compose global stat.
    s_counter = Counter()
    for name, spectrum_ctr in speaker_spectrums.items():
        s_counter[name] = len(spectrum_ctr)

    s_counter_common = CounterService.from_most_common(s_counter, n=20)
    draw_hist_plot(data=CounterService.to_melt_list(ctr=s_counter_common),
                   desc='Spectrums Per Speaker',
                   save_png_path=join(TEST_DIR, f"spectrums_per_speaker.png"),
                   x_min=-1, x_max=len(s_counter_common),
                   asp_hor=14, asp_ver=2, show=False)
