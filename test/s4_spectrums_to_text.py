from os.path import join

from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from e_pairs.spectrum.presets import PROMPT_PRESETS
from utils import DATA_DIR


spectrum_cfg = SpectrumConfig()
X = NpzUtils.load(spectrum_cfg.features_norm)
fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
prompts = PROMPT_PRESETS["most_imported_limited_5"](X, fcp_api)

print(prompts)
