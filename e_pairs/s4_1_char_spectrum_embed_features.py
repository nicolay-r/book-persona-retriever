from os.path import join

from api.my import MyAPI
from core.spectrums.text_source import iter_all
from core.spectrums_annot import annot_to_min_max_grouped, annot_spectrums_in_text
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR


if __name__ == '__main__':

    my_api = MyAPI()
    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    spectrum_cfg = SpectrumConfig()

    speaker_spectrums_dict = annot_spectrums_in_text(
        texts_and_speakervars_iter=iter_all(speakers=my_api.read_speakers(),
                                            my_api=my_api,
                                            spectrum_cfg=spectrum_cfg),
        rev_spectrums=fcp_api.reversed_spectrums())

    # Saving.
    spectrums_count = len(fcp_api._lexicon) + 1
    data = {
        spectrum_cfg.features_norm: lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count,
            ind_func=FcpApi.spectrum_to_ind),
        spectrum_cfg.features_diff: lambda speakers: annot_to_min_max_grouped(
            speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count,
            ind_func=FcpApi.spectrum_to_ind),
    }

    for x_path, f in data.items():
        x, y = [], []
        d = f(speaker_spectrums_dict)

        for s_name, s_ctr in d.items():
            x.append(s_ctr)
            y.append(s_name)

        NpzUtils.save(data=x, target=x_path)
        print(f"Saved: {x_path}")
        NpzUtils.save(data=y, target=spectrum_cfg.speakers)
        print(f"Saved: {spectrum_cfg.speakers}")
