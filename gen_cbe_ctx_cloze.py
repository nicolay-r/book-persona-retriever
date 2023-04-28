# Ctx level, cloze
import json
from os import makedirs
from os.path import basename, join, exists

from tqdm import tqdm

from utils_cbe import CBEApi
from utils_pg19 import PG19Api

quiz_paths = [
    "./data/charembench/data/ctx_level/cloze.json",
    "./data/charembench/data/ctx_level/qa.json"
]

output = "./data/charemberch-prepared"

prompt = "We consider the book ``{book_title}''." \
         "You're given a task to replace ___ with the particular character in following context: {text} " \
         "Select the from the following list: {char_list}."

# Create target directory if the latter does not exist.
if not exists(output):
    makedirs(output)

# reading char_map.
cbe_api = CBEApi()
cbe_api.read()

# reading pg-19 metadata.
pg19_api = PG19Api()
pg19_api.read("data/pg19/metadata.csv")

# reading char_map.
for fp in quiz_paths:
    with open(fp, "r") as input_file:

        # output filepath.
        ofp = join(output, basename(fp))
        with open(ofp, 'w') as output_file:

            content = json.load(input_file)
            for task in tqdm(content["data"]):
                task_data, speaker_id = task
                text, choice_ids = task_data

                book_id = speaker_id.split('_')[0]
                speaker_choice = [cbe_api.get_char_name(choice_id) for choice_id in choice_ids]

                # extracting book title
                book_title = pg19_api.find_book_title(book_id)
                if book_title is None:
                    continue

                line = prompt.format(book_title=book_title,
                                     text=cbe_api.replace_characters_in_text(text),
                                     char_list=", ".join(speaker_choice))

                line += " The correct answer is {}".format(cbe_api.get_char_name(speaker_id))

                output_file.write("{}\n".format(line))
