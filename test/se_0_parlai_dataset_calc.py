from collections import Counter
from os.path import join
from zipfile import ZipFile

from api.se import SEApi

dataset_names = [
    "dataset_parlai_train__hla-cand.txt.zip",
    "dataset_parlai_valid__hla-cand.txt.zip"
]

for dataset_name in dataset_names:
    c = Counter()
    with ZipFile(join(SEApi.books_storage, dataset_name), 'r') as myzip:
        prev_line_index = None
        with myzip.open(myzip.filelist[0]) as f:
            for line in f.readlines():
                line_index = int(line.split()[0])
                if prev_line_index is None or (prev_line_index >= line_index):
                    c["lines"] += 1
                prev_line_index = line_index
        print(dataset_name)
        print(c["lines"])
