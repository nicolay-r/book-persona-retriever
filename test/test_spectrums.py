from os.path import join

from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_hla import HlaExperimentConfig
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.spectrum.presets import PROMPT_PRESETS
from utils import DATA_DIR


spectrum_cfg = SpectrumConfig()
xn = NpzUtils.load(spectrum_cfg.features_norm)
xc = NpzUtils.load(spectrum_cfg.features_diff)
y = NpzUtils.load(spectrum_cfg.speakers)

print(xn)
print(xc)
print(y)

fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
prompts = PROMPT_PRESETS[HlaExperimentConfig.hla_spectrum_preset](xn, xc, fcp_api)
