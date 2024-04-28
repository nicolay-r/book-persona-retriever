from os.path import join

from core.spectrums.io_utils import SpectrumIOUtils
from core.spectrums.presets import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR
from utils_my import MyAPI


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig(books_storage=MyAPI.books_storage)

    X_norm = NpzUtils.load(spectrum_cfg.features_norm)
    X_diff = NpzUtils.load(spectrum_cfg.features_diff)
    y = NpzUtils.load(spectrum_cfg.speakers)

    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    prompts, weights = PROMPT_PRESETS[MyAPI.hla_spectrum_preset](X_norm, X_diff, fcp_api)

    SpectrumIOUtils.write(filepath=MyAPI.hla_prompts_filepath,
                          speaker_names=y, speaker_prompts=prompts, weights=weights)