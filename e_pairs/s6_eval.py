import sqlite3

import numpy as np
import pandas as pd
from parlai.core.metrics import BleuMetric, F1Metric, RougeMetric


def calc(compute_func):
    results = []
    for r_id, response in responses.items():
        if r_id in labels:
            label = labels[r_id]
            computed_result = compute_func(response, label)
            results.append(float(computed_result)
                           if not isinstance(computed_result, tuple)
                           else [float(r) for r in computed_result])
    return np.average(results, axis=0)


if __name__ == '__main__':

    limit = 3136
    table = "original"

    con = sqlite3.connect("data/eval-llm/answers.sqlite3")
    responses = {}

    ####################
    # Extract responses.
    ####################
    cursor = con.cursor()
    cursor.execute(f'SELECT * FROM {table}')
    for row in cursor:
        r_id, response = row
        responses[int(r_id)] = response

    #################
    # Extract labels.
    #################
    df = pd.read_csv("data/eval-llm/valid_original_no-cand-labeled.csv", sep="\t")
    labels = {}
    for i, r in list(df.iterrows())[:limit]:
        d = r.to_dict()
        labels[d["id"]] = d["label"]

        r = {
            "bleu-1": calc(lambda r, l: BleuMetric.compute(guess=r, answers=[l], k=1)),
            "bleu-2": calc(lambda r, l: BleuMetric.compute(guess=r, answers=[l], k=2)),
            "bleu-3": calc(lambda r, l: BleuMetric.compute(guess=r, answers=[l], k=3)),
            "bleu-4": calc(lambda r, l: BleuMetric.compute(guess=r, answers=[l], k=4)),
            "f1": calc(lambda r, l: F1Metric.compute(guess=r, answers=[l], expose_p_and_r=True)),
            "rouge": calc(lambda r, l: RougeMetric.compute_many(guess=r, answers=[l])),
        }

        content = [
            r["bleu-1"],
            r["bleu-2"],
            r["bleu-3"],
            r["bleu-4"],
            "",             # ppl
            "",             # en-acc
            r["f1"][2],
            r["f1"][1],
            r["f1"][0],
            r["rouge"][0],
            r["rouge"][1],
            r["rouge"][2]
        ]

        print(table)
        print("\t".join([str(v) for v in content]))
