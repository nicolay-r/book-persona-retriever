from os.path import join

from api.my import MyAPI
from core.spectrums.io_utils import SpectrumIOUtils
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.hla_models.spectrum.presets import PROMPT_PRESETS
from utils import DATA_DIR


if __name__ == '__main__':

    spectrum_cfg = SpectrumConfig()

    X_norm = NpzUtils.load(spectrum_cfg.features_norm)
    X_diff = NpzUtils.load(spectrum_cfg.features_diff)
    y = NpzUtils.load(spectrum_cfg.speakers)

    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
    hla_cfg = HlaExperimentConfig(books_storage=MyAPI.books_storage)

    prompts, weights = PROMPT_PRESETS[hla_cfg.hla_spectrum_preset](X_norm, X_diff, fcp_api)

    target = hla_cfg.hla_prompts_filepath
    SpectrumIOUtils.write(filepath=target, speaker_names=y, speaker_prompts=prompts, weights=weights)
    print(f"Saved: {target}")
