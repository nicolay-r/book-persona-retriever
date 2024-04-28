from os.path import join

from core.spectrums.presets import PROMPT_PRESETS
from core.utils_npz import NpzUtils
from e_pairs.api_fcp import FcpApi
from e_pairs.cfg_spectrum import SpectrumConfig
from utils import DATA_DIR
from utils_my import MyAPI


spectrum_cfg = SpectrumConfig(books_storage=MyAPI.books_storage)
X = NpzUtils.load(spectrum_cfg.features_norm)
fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))
prompts = PROMPT_PRESETS["most_imported_limited_5"](X, fcp_api)

print(prompts)
