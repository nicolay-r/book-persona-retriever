import argparse
from collections import Counter
from os.path import join

from core.database.sqlite3_api import SQLiteService
from utils import CsvService
from utils_ceb import CEBApi
from utils_em import EMApi


def iter_etalon_results(iter_lines, filter_speaker_id=None, out_filter_mask=None):
    for rid, line in enumerate(iter_lines):
        speaker_id, speaker_name, _ = line

        if filter_speaker_id is not None:
            # We filter those who were not in list of the predefined characters.
            filtered = filter_speaker_id(speaker_id)
            out_filter_mask.append(filtered)
            if not filtered:
                continue

        yield speaker_name


def iter_predict(iter_lines, character_names, filter_mask=None, out_ctr=None):

    for line_ind, line in enumerate(iter_lines):

        # Optionally skip the line if there is a filter mask.
        if filter_mask is not None and not filter_mask[line_ind]:
            continue

        _, _, response = line
        response = response.strip()

        # Seeking for the result name in the response.
        names_found = []
        for char_name in character_names:
            if char_name in response:
                names_found.append(char_name)

        yield names_found[0] if len(names_found) == 1 else "-"

        # Filling with the logging information if needed.
        if out_ctr is not None:
            out_ctr["defined"] += (len(names_found) == 1)
            out_ctr["undefined"] += (len(names_found) != 1)
            out_ctr["total"] += 1


def eval(etalon, predicted, p_ctr):
    assert(isinstance(p_ctr, Counter))

    c = Counter()

    for i in range(len(etalon)):
        c["matched"] += etalon[i] == predicted[i]

    print("------")
    print("Defined", round(p_ctr["defined"] / p_ctr["total"], 2))
    print("Hits@1-defined", round(c["matched"] / p_ctr["defined"], 2))
    print("Hits@1-total", round(c["matched"] / p_ctr["total"], 2))


parser = argparse.ArgumentParser()

parser.add_argument('--predict', dest='predict',
                    default=join(EMApi.output_dir, f"./results/1184_10_rag.csv_mistralai_Mistral-7B-Instruct-v0.1.sqlite:contents"))
parser.add_argument('--etalon', dest='etalon',
                    default=join(EMApi.output_dir, f"dialogue-ctx-default.csv"))
parser.add_argument('--characters', dest='characters', type=list,
                    default=["1184_0", "1184_3", "1184_4", "1184_5", "1184_6", "1184_7", "1184_10", "1184_12", "1184_14", "1184_17"])

args = parser.parse_args()

ceb_api = CEBApi()
ceb_api.read_char_map()

# Results.
filter_mask = []
etalon_names = list(iter_etalon_results(
    iter_lines=CsvService.read(target=args.etalon, delimiter='\t', skip_header=True),
    filter_speaker_id=lambda speaker_id: speaker_id in args.characters,
    out_filter_mask=filter_mask))

p_ctr = Counter()

target, table_name = args.predict.split(':')
predict_names = list(iter_predict(
    iter_lines=SQLiteService.iter_content(target=target, table=table_name),
    character_names=[ceb_api.get_char_name(f"{EMApi.book_id}_{c}") for c in EMApi.chars],
    filter_mask=filter_mask,
    out_ctr=p_ctr
))

assert(len(etalon_names) == len(predict_names))

eval(etalon=etalon_names, predicted=predict_names, p_ctr=p_ctr)
