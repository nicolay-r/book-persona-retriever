from core.spectrums.io_utils import SpectrumIOUtils
from utils_my import MyAPI


r = SpectrumIOUtils.read(filepaths=MyAPI.hla_prompts_filepath.format(MyAPI.hla_spectrum_preset))
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