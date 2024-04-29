from api.my import MyAPI
from e_pairs.cfg_hla import HlaExperimentConfig
from core.spectrums.io_utils import SpectrumIOUtils


hla_cfg = HlaExperimentConfig(books_storage=MyAPI.books_storage)
r = SpectrumIOUtils.read(filepaths=hla_cfg.hla_prompts_filepath.format(hla_cfg.hla_spectrum_preset))
e = set()
same = 0
same_speakers = []
for k, v in r.items():
    vv = ",".join(v["prompts"])
    if vv in e:
        same += 1
        same_speakers.append(k)
    e.add(vv)

print(same)
print(len(r.items()))
print(same_speakers)