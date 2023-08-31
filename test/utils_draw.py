from collections import Counter
from core.plot import draw_spectrum_barplot


def draw_spectrums_stat(speaker_spectrum_counters, save_png_filepath, fcp_api, asp_hor=2, asp_ver=8,
                        spectrums_set=None, top_bars_count=None, bottom_bars_count=None):
    """ Drawing based on counter.
    """

    def bap_to_number(bap):
        return bap.split('-')[0]

    s_counter = Counter()
    for spectrum_ctr in speaker_spectrum_counters:
        for spectrum_name, value in spectrum_ctr.items():

            # Optional filtering.
            if spectrums_set is not None:
                # "BAP56" -> "56"
                if int(bap_to_number(spectrum_name)[3:]) not in spectrums_set:
                    continue

            s_counter[spectrum_name] += value if 'high' in spectrum_name else -value

    if len(s_counter) != 0:
        draw_spectrum_barplot(s_counter,
                              x_name="bap",
                              y_name="cat",
                              val_to_x=lambda k: int(''.join([ch for ch in k if ch.isdigit()])),
                              # BAP + meaning
                              val_to_cat_caption=lambda k: bap_to_number(k) + ' ' + str(fcp_api.find_by_id(bap_to_number(k))),
                              top_bars_count=top_bars_count,
                              bottom_bars_count=bottom_bars_count,
                              asp_ver=asp_ver,
                              asp_hor=asp_hor,
                              show=False,
                              save_png_path=save_png_filepath)
