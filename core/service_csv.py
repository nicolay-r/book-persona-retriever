import csv
from collections import Counter


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
