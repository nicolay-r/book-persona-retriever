import csv
import os
from collections import Counter
from os.path import join

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = join(PROJECT_DIR, "./data/")
RANK_DATASET_DIR = join(DATA_DIR, "hla_books")
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


class TextService:

    @staticmethod
    def write(target, lines_it):
        counter = Counter()
        with open(target, "w") as o:
            for line in lines_it:
                o.write(line + "\n")
                counter["total"] += 1

        print("Saved: {}".format(target))
        print("Rows written: {}".format(counter["total"]))


class CsvService:

    @staticmethod
    def write(target, lines_it, header=None, notify=True):
        assert(isinstance(header, list) or header is None)

        counter = Counter()
        with open(target, "w") as f:
            w = csv.writer(f, delimiter="\t", quotechar='"', quoting=csv.QUOTE_MINIMAL)

            if header is not None:
                w.writerow(header)

            for content in lines_it:
                w.writerow(content)
                counter["written"] += 1

        if notify:
            print(f"Saved: {target}")
            print("Total rows: {}".format(counter["written"]))

    @staticmethod
    def read(target, delimiter='\t', quotechar='"', skip_header=False, cols=None, return_row_ids=False):
        assert(isinstance(cols, list))

        header = None
        with open(target, newline='\n') as f:
            for row_id, row in enumerate(csv.reader(f, delimiter=delimiter, quotechar=quotechar)):
                if skip_header and row_id == 0:
                    header = row
                    continue

                # Determine the content we wish to return.
                if cols is None:
                    content = row
                else:
                    row_d = {header[col_name]: value for col_name, value in enumerate(row)}
                    content = [row_d[col_name] for col_name in cols]

                # Optionally attach row_id to the content.
                yield [row_id] + content if return_row_ids else content