import csv
import os
from os.path import join

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
RANK_DATASET_DIR = join(PROJECT_DIR, "data/hla_books")
CACHE_DIR = join(PROJECT_DIR, "./.cache")


def cat_files(source_filepaths, target_filepath):
    assert(isinstance(source_filepaths, list))

    with open(target_filepath, 'w') as outfile:
        for filename in source_filepaths:
            with open(filename) as infile:
                for line in infile:
                    outfile.write(line)


def range_middle(n):
    return [round(n/2)]


def range_exclude_middle(n):
    middle = range_middle(n)[0]
    return [i for i in range(n) if i != middle]


class CsvService:

    @staticmethod
    def write(target, lines_it):
        with open(target, "w") as f:
            w = csv.writer(f, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for content in lines_it:
                w.writerow(content)

    @staticmethod
    def read(target, delimiter='\t', quotechar='"', skip_header=False):
        with open(target, newline='\n') as f:
            for i, row in enumerate(csv.reader(f, delimiter=delimiter, quotechar=quotechar)):
                if skip_header and i == 0:
                    continue
                yield row
