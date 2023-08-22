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
    "ppl",
    "token_acc",
    "rouge_1",
    "rouge_2",
    "rouge_L",
]

result_metrics_generative = [
    "bleu-1",
    "bleu-2",
    "bleu-3",
    "bleu-4",
    "ppl",
    "token_acc",
    "f1",
    "precision",
    "recall",
    "rouge_1",
    "rouge_2",
    "rouge_L",
]

with open("file.txt", "r") as f:
    contents = f.read()
    contents = contents.replace("\n", " ").replace("\\", " ").strip()
    tokens = contents.split()
    r = {tokens[i]: tokens[i+1] for i in range(0, len(tokens), 2)}
    line = [r[m] if m in r else "" for m in result_metrics_generative]
    print("\t".join(line))