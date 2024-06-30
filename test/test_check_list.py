from api.ldc import LdcAPI
from e_pairs.cfg_hla import HlaExperimentConfig


s = set()
hla_cfg = HlaExperimentConfig(books_storage=LdcAPI.books_storage)
print(hla_cfg.hla_prompts_filepath)
with open(hla_cfg.hla_prompts_filepath, "r") as f:
    for line in f.readlines():
        line = line.split(":")[1]
        words = [s.strip() for s in line.split(",")]
        for w in words:
            s.add(w)

print("Total different words:", len(s))
