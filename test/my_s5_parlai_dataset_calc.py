from collections import Counter
from os import path
from zipfile import ZipFile

from utils_my import MyAPI


my_api = MyAPI()
dataset_names = [
    "dataset_parlai_train_original.txt.zip",
    "dataset_parlai_train_spectrum_clustered.txt.zip",
    "dataset_parlai_valid_original.txt.zip",
    "dataset_parlai_valid_spectrum.txt.zip",
]

for dataset_name in dataset_names:
    c = Counter()
    with ZipFile(path.join(MyAPI.books_storage, dataset_name), 'r') as myzip:
        prev_line_index = None
        with myzip.open(myzip.filelist[0]) as f:
            for line in f.readlines():
                line_index = int(line.split()[0])
                if prev_line_index is None or (prev_line_index > line_index):
                    c["lines"] += 1
                prev_line_index = line_index
        print(dataset_name)
        print(c["lines"])
