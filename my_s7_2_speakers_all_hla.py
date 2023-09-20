import os
from os.path import join, exists

from core.spectrums.text_source import iter_all
from core.spectrums_annot import annot_spectrums_in_text, annot_to_min_max_grouped
from core.utils_npz import NpzUtils
from utils_ceb import CEBApi
from utils_fcp import FcpApi
from utils_my import MyAPI

############################################
# SPECTRUMS: Calculation.
############################################
my_api = MyAPI()
fcp_api = FcpApi()
ceb_api = CEBApi()
ceb_api.read_char_map()
speakers = list(ceb_api.iter_chars())
print("Speakers considered: {}".format(len(speakers)))
speaker_spectrums_dict = annot_spectrums_in_text(
    texts_and_speakervars_iter=iter_all(speakers=speakers, my_api=my_api),
    rev_spectrums=fcp_api.reversed_spectrums())

print("speaker spectrums dict len:", len(speaker_spectrums_dict))

# Saving.
spectrums_count = len(fcp_api._lexicon)+1
data = {
    "speakers-all-norm.npz": lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=True, as_vectors=True, spectrums_count=spectrums_count),
    "speakers-all-diff.npz": lambda speakers: annot_to_min_max_grouped(
        speakers, do_norm=False, as_vectors=True, spectrums_count=spectrums_count),
}

# Create dir if not exists.
if not exists(MyAPI.selected_output_dir):
    os.makedirs(MyAPI.selected_output_dir)

# Collect and write data.
for x_path, f in data.items():
    x, y = [], []
    d = f(speaker_spectrums_dict)

    for spectrum_name, ctr in d.items():
        x.append(ctr)
        y.append(spectrum_name)

    NpzUtils.save(data=x, target=join(MyAPI.selected_output_dir, x_path))
    NpzUtils.save(data=y, target=join(MyAPI.selected_output_dir, "speaker-all-names.npz"))
