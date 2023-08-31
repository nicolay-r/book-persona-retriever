from core.spectrums.text_source import iter_all
from core.spectrums_annot import annot_spectrums_in_text, annot_to_min_max_grouped
from core.utils_npz import NpzUtils
from utils_fcp import FcpApi
from utils_my import MyAPI


my_api = MyAPI()
fcp_api = FcpApi()
speaker_spectrums_dict = annot_spectrums_in_text(
    texts_and_speakervars_iter=iter_all(speakers=my_api.read_speakers(), my_api=my_api),
    rev_spectrums=fcp_api.reversed_spectrums())

# Saving.
spectrums_count = len(fcp_api._lexicon)+1
data = {
    MyAPI.spectrum_features_norm: lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count),
    MyAPI.spectrum_features_diff: lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count),
}

for x_path, f in data.items():
    x, y = [], []
    d = f(speaker_spectrums_dict)

    for s_name, s_ctr in d.items():
        x.append(s_ctr)
        y.append(s_name)

    NpzUtils.save(data=x, target=x_path)
    NpzUtils.save(data=y, target=MyAPI.spectrum_speakers)
