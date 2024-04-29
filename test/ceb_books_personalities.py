from tqdm import tqdm
from os import listdir
from os.path import isfile, join

from api.my import MyAPI
from e_pairs.api_fcp import FcpApi
from utils import DATA_DIR


if __name__ == '__main__':

    fcp_api = FcpApi(personalities_path=join(DATA_DIR, "personalities.txt"))

    d = fcp_api.extract_as_lexicon()
    for key, value in d.items():
        print(key, value)

    in_dir = MyAPI.books_storage_en
    f_names = [f for f in listdir(in_dir) if isfile(join(in_dir, f))]

    lexicon_entries = [next(iter(v["low"])) for v in d.values()] + [next(iter(v["high"])) for v in d.values()]
    print(lexicon_entries)

    c = 0
    stat = {}
    for f_name in tqdm(f_names):
        with open(join(in_dir, f_name), "r") as f:
            for line in f.readlines():
                line_words = line.split(' ')
                for w in line_words:
                    if w in lexicon_entries:
                        if w not in stat:
                            stat[w] = 0
                        stat[w] += 1

    for k, v in sorted(stat.items(), key=lambda item: item[1]):
        print(k, v)
    print("Entries matched: {}".format(sum(stat.values())))

