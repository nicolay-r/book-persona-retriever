import json
from os import makedirs
from os.path import basename, join, exists

from tqdm import tqdm

from utils_ceb import CEBApi
from utils_pg19 import PG19Api

quiz_paths = [
    "./data/charembench/data/char_level/ident.json",
]

output = "./data/charemberch-prepared"
# Create target directory if the latter does not exist.
if not exists(output):
    makedirs(output)

# reading char_map
cbe_api = CEBApi()
cbe_api.read()

# reading pg-19 metadata.
pg19_api = PG19Api()
pg19_api.read("data/pg19/metadata.csv")

# reading char_map
for fp in quiz_paths:
    with open(fp, "r") as f:
        content = json.load(f)

        # output filepath.
        ofp = join(output, basename(fp))
        with open(ofp, 'w') as output_file:

            for task in tqdm(content["data"]):
                speaker_ids, is_male = task
                book_ids = [speaker_id.split('_')[0] for speaker_id in speaker_ids]
                book_titles = [pg19_api.find_book_title(book_id) for book_id in book_ids]

                book_not_found = False
                for title in book_titles:
                    if title is None:
                        book_not_found = True
                        break

                if book_not_found:
                    continue

                line = '\t'.join([
                    # Join character information.
                    ' and '.join([
                        "Character `{chr_name}` from the `{book_title}`".format(
                            chr_name=cbe_api.get_char_name(speaker_ids[index], index),
                            book_title=book_titles[index])
                        for index in range(len(speaker_ids))
                    ]),
                    ", are they same? Yes or no?",
                    "Yes" if is_male else "No"
                ])

                output_file.write("{}\n".format(line))
