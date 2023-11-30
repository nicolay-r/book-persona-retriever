from collections import Counter
from utils_ceb import CEBApi
from utils_pg19 import PG19Api

c = Counter()
with open("data/llm_em/dataset.txt", "r") as f:
    for line in f.readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        args = line.split(": ")
        meta = args[0]
        if meta == "UNKN-X":
            continue
        book_id = meta.split("_")[0]
        c[book_id] += 1

pg19 = PG19Api()
pg19.read()

for b_id, count in sorted(c.items(), key=lambda item: int(item[1]), reverse=True)[:50]:
    title = pg19.find_book_title(book_id=b_id)
    print(count, title, b_id)


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


def iter_book_utterances(requested_book_id):
    with open("data/llm_em/dataset.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            args = line.split(": ")
            meta = args[0]
            if meta == "UNKN-X":
                continue
            book_id = meta.split("_")[0]
            if int(book_id) == requested_book_id:
                yield line


book_id_filter = 1184
filtered_dataset = f"data/llm_em/{book_id_filter}.txt"
with open("data/llm_em/dataset.txt", "r") as f:
    with open(filtered_dataset, "w") as o:
        for line in iter_book_utterances(book_id_filter):
            o.write(line + "\n")

c = calc_speakers_stat(dataset_path=filtered_dataset)

ceb_api = CEBApi()
ceb_api.read_char_map()

for cid in c.keys():
    print(cid, ceb_api.get_char_names(cid))
