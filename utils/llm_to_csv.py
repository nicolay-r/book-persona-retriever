import pandas as pd
from os.path import dirname, realpath, join

root = join(dirname(realpath(__file__)), "../data/eval-llm/")

for t in ["original", "spectrum"]:
    template = f"valid_{t}_no-cand"
    df = pd.read_csv(join(root, f"{template}.txt"), header=None, sep="\t")
    df.index.name = "id"
    df.columns = ["text_a", "label"]
    df.to_csv(join(root, f"{template}-labeled.csv"), sep="\t")
