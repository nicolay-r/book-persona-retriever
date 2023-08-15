# This script allows to parse the following lines:

result_metrics = [
    "hits@1",
    "hits@5",
    "hits@10",
    "f1",
    "mrr",
    "rank",
    "precision",
    "recall",
    "bleu-4",
]

with open("file.txt", "r") as f:
    contents = f.read()
    contents = contents.replace("\n", " ").replace("\\", " ").strip()
    tokens = contents.split()
    r = {tokens[i]: tokens[i+1] for i in range(0, len(tokens), 2)}
    line = [r[m] if m in r else "" for m in result_metrics]
    print("\t".join(line))