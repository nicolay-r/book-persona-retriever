import os
from os.path import join, exists

from api.my import MyAPI
from api.se import SEApi
from core.spectrums.text_source import iter_all
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.hla_models.spectrum.annot import annot_to_min_max_grouped, annot_spectrums_in_text
from test.const import MOST_DISTINCTIVE
from test.utils_draw import draw_spectrums_stat
from utils import DATA_DIR


if __name__ == '__main__':

    se_api = SEApi()
    my_api = MyAPI()
    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    spectrum_cfg = SpectrumConfig()
    speaker_spectrums_dict = annot_spectrums_in_text(
        texts_and_speakervars_iter=iter_all(speakers=se_api.predefined_speakers,
                                            my_api=my_api,
                                            spectrum_cfg=spectrum_cfg),
        rev_spectrums=fcp_api.reversed_spectrums())

    print("speaker spectrums dict len:", len(speaker_spectrums_dict))

    # Saving.
    spectrums_count = len(fcp_api._lexicon)+1
    data = {
        "speakers-selected-norm.npz": lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count,
            ind_func=fcp_api.spectrum_to_ind),
        "speakers-selected-diff.npz": lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count,
            ind_func=fcp_api.spectrum_to_ind),
    }

    # Create dir if not exists.
    if not exists(SEApi.selected_output_dir):
        os.makedirs(SEApi.selected_output_dir)

    for x_path, f in data.items():
        x, y = [], []
        d = f(speaker_spectrums_dict)

        for spectrum_name, ctr in d.items():
            x.append(ctr)
            y.append(spectrum_name)

        NpzUtils.save(data=x, target=join(se_api.selected_output_dir, x_path))
        NpzUtils.save(data=y, target=join(se_api.selected_output_dir, "speaker-selected-names.npz"))

    for speaker_id, ctr in speaker_spectrums_dict.items():
        draw_spectrums_stat(speaker_spectrum_counters=[ctr], fcp_api=fcp_api,
                            asp_ver=6, asp_hor=2, top_bars_count=8, bottom_bars_count=8,
                            spectrums_exclude=[70, 98, 117, 84, 125, 211, 69, 161, 119, 97, 54],
                            save_png_filepath=join(se_api.selected_output_dir,
                                                   f"speakers-selected-spectrums-{speaker_id}.png"))

    for speaker_id, ctr in speaker_spectrums_dict.items():
        draw_spectrums_stat(speaker_spectrum_counters=[ctr], fcp_api=fcp_api,
                            asp_ver=6, asp_hor=2, spectrums_keep=MOST_DISTINCTIVE, top_bars_count=8, bottom_bars_count=8,
                            save_png_filepath=join(se_api.selected_output_dir,
                                                   f"speakers-selected-spectrums-{speaker_id}-most-distinctive.png"))
