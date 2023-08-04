import json
from os import makedirs
from os.path import basename, join, exists

from tqdm import tqdm

from utils_ceb import CEBApi
from utils_pg19 import PG19Api

quiz_paths = [
    "./data/charembench/data/char_level/role.json",
]

output = "./data/charemberch-prepared"
# Create target directory if the latter does not exist.
if not exists(output):
    makedirs(output)

# reading char_map
ceb_api = CEBApi()
ceb_api.read_char_map()

# reading pg-19 metadata.
pg19_api = PG19Api()
pg19_api.read("data/pg19/metadata.csv")

books_missed = 0
# reading char_map
for fp in quiz_paths:
    with open(fp, "r") as f:
        content = json.load(f)

        # output filepath.
        ofp = join(output, basename(fp))
        with open(ofp, 'w') as output_file:

            for task in tqdm(content["data"]):
                speaker_id = task["char_id"]
                candidates = task["candidates"]
                answer = task["answer"]
                book_id = speaker_id.split('_')[0]

                # extracting book title
                book_title = pg19_api.find_book_title(book_id)
                if book_title is None:
                    books_missed += 1
                    continue

                line = '\t'.join([
                    "{char_name} from {book_title}".format(char_name=ceb_api.get_char_name(speaker_id),
                                                           book_title=book_title),
                    " ".join(candidates),
                    answer
                ])

                output_file.write("{}\n".format(line))

print("books missed: {}".format(books_missed))
