##########################################
# This is a dictionary of preset functions
##########################################
from core.spectrums.to_prompts import filter_by_non_zero, to_prompts_top_k, to_prompts
from core.utils_npz import NpzUtils
from utils_my import MyAPI

PROMPT_PRESETS = {
    # This is a first revision when we keep everything.
    "prompt_original": lambda X, fcp_api: to_prompts(X=X, fcp_api=fcp_api),
    "prompt_top_k_10": lambda X_norm, X_diff, fcp_api: to_prompts_top_k(
        X_norm=X_norm, X_diff=X_diff, fcp_api=fcp_api, k=10),
    "prompt_top_k_8": lambda X_norm, X_diff, fcp_api: to_prompts_top_k(
        X_norm=X_norm, X_diff=X_diff, fcp_api=fcp_api, k=8),
    "prompt_top_k_5": lambda X_norm, X_diff, fcp_api: to_prompts_top_k(
        X_norm=X_norm, X_diff=X_diff, fcp_api=fcp_api, k=5),
    "prompt_top_k_8_limited": lambda X_norm, X_diff, fcp_api: to_prompts_top_k(
        X_norm=X_norm, X_diff=X_diff, fcp_api=fcp_api, k=8, limit=MyAPI.hla_spectrums_limit),
    "prompt_top_k_5_limited": lambda X_norm, X_diff, fcp_api: to_prompts_top_k(
        X_norm=X_norm, X_diff=X_diff, fcp_api=fcp_api, k=5, limit=MyAPI.hla_spectrums_limit),
}

FILTER_PRESETS = {
    "original-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=50, paint_func=None, gt=True),
    "all-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=None, paint_func=None, gt=True),
    "z-geq10-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=9, paint_func=None, gt=True),
    "z-geq5-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=4, paint_func=None, gt=True),
    "z-ge50-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=50, paint_func=None, gt=True),
    "z-le2-no-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=2, paint_func=None, gt=False),
    "z-le2-color": lambda X, y: filter_by_non_zero(
        X=X, y=y, z=NpzUtils.load(MyAPI.spectrum_features_norm), threshold=2,
        paint_func=lambda nzc: str(nzc) if nzc <= 2 else "others", gt=False)
}
