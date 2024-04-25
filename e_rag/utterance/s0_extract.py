import argparse
from collections import Counter
from os.path import join

from core.service_txt import TextService
from e_rag.utils_em import EMApi
from utils_ceb import CEBApi
from utils_pg19 import PG19Api


def calc_speakers_stat(dataset_path):
    c = Counter()
    with open(dataset_path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            args = line.split(": ")
            meta = args[0]
            if meta == "UNKN-X":
                continue
            c[meta] += 1
    return c


def iter_annotated_utterances(lines_it, is_filter_book_id):
    for line in lines_it:
        line = line.strip()
        if len(line) == 0:
            continue
        args = line.split(": ")
        meta = args[0]
        if meta == "UNKN-X":
            continue
        params = meta.split("_")
        if len(params) == 1:
            continue
        book_id = params[0]
        if is_filter_book_id(int(book_id)):
            yield line


def calculate_utterances_per_book_stat(dataset_filepath):
    counter = Counter()
    with open(dataset_filepath, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            meta = line.split(": ")[0]
            if meta == "UNKN-X":
                continue
            book_id = meta.split("_")[0]
            counter[book_id] += 1

    return counter


def iter_utterances(filepath):
    with open(filepath, "r") as f:
        return iter_annotated_utterances(
            lines_it=f.readlines(), is_filter_book_id=lambda book_id: book_id == EMApi.book_id)


parser = argparse.ArgumentParser(description="Composing Prompts with RAG technique")

parser.add_argument('--dataset', dest='dataset', type=str, default=join(EMApi.output_dir, "dataset.txt"))
parser.add_argument('--output', dest='output', type=str, default=join(EMApi.output_dir, f"./{EMApi.book_id}.txt"))

args = parser.parse_args()

pg19 = PG19Api()
pg19.read()

# for b_id, count in sorted(c.items(), key=lambda item: int(item[1]), reverse=True)[:50]:
#     title = pg19.find_book_title(book_id=b_id)
#     print(count, title, b_id)

TextService.write(target=args.output, lines_it=iter_utterances(args.dataset))
counter = calc_speakers_stat(dataset_path=args.output)

ceb_api = CEBApi()
ceb_api.read_char_map()
# for cid in c.keys():
#     print(cid, ceb_api.get_char_names(cid))
