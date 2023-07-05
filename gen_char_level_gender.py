import json
from os import makedirs
from os.path import basename, join, exists

from tqdm import tqdm

from utils_ceb import CEBApi
from utils_pg19 import PG19Api

# reading char_map
ceb_api = CEBApi()
ceb_api.read_char_map()

quiz_paths = [
    ceb_api.gender_meta_path
]

output = "./data/charemberch-prepared"
# Create target directory if the latter does not exist.
if not exists(output):
    makedirs(output)

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
                speaker_id, is_male = task
                book_id = speaker_id.split('_')[0]

                # extracting book title
                book_title = pg19_api.find_book_title(book_id)
                if book_title is None:
                    continue

                line = '\t'.join([
                    "{char_name} from {book_title}".format(char_name=ceb_api.get_char_name(speaker_id),
                                                           book_title=book_title),
                    "Is Male?",
                    "Yes" if is_male else "No"
                ])

                output_file.write("{}\n".format(line))
