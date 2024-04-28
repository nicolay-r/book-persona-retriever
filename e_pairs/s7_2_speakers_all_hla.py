import os
from os.path import join, exists

from core.spectrums.text_source import iter_all
from core.spectrums_annot import annot_spectrums_in_text, annot_to_min_max_grouped
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR
from utils_ceb import CEBApi
from utils_my import MyAPI


if __name__ == '__main__':

    my_api = MyAPI()
    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    spectrum_cfg = SpectrumConfig(books_storage=MyAPI.books_storage)

    ceb_api.read_char_map()
    speakers = list(ceb_api.iter_chars())
    print("Speakers considered: {}".format(len(speakers)))
    speaker_spectrums_dict = annot_spectrums_in_text(
        texts_and_speakervars_iter=iter_all(speakers=speakers, my_api=my_api, spectrum_cfg=spectrum_cfg),
        rev_spectrums=fcp_api.reversed_spectrums())

    print("speaker spectrums dict len:", len(speaker_spectrums_dict))

    # Saving.
    spectrums_count = len(fcp_api._lexicon)+1
    data = {
        "speakers-all-norm.npz": lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count, ind_func=FcpApi.spectrum_to_ind),
        "speakers-all-diff.npz": lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count, ind_func=FcpApi.spectrum_to_ind),
    }

    # Create dir if not exists.
    output_dir = join(DATA_DIR, "./selected_books_annot/")
    if not exists(output_dir):
        os.makedirs(output_dir)

    # Collect and write data.
    for x_path, f in data.items():
        x, y = [], []
        d = f(speaker_spectrums_dict)

        for spectrum_name, ctr in d.items():
            x.append(ctr)
            y.append(spectrum_name)

        NpzUtils.save(data=x, target=join(output_dir, x_path))
        NpzUtils.save(data=y, target=join(output_dir, "speaker-all-names.npz"))
