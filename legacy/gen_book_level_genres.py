# Ctx level, cloze
import json
from os import makedirs
from os.path import basename, join, exists

from tqdm import tqdm

from utils_ceb import CEBApi
from utils_pg19 import PG19Api

quiz_paths = {
    "./data/charembench/data/book_level/genre-19th_century.json":
        "Does character {character} belong to a 19th century book genre?",
    "./data/charembench/data/book_level/genre-adventure_stories.json":
        "Does character {character} belong to adventure stories book genre?",
    "./data/charembench/data/book_level/genre-detective_and_mystery_stories.json":
        "Does character {character} belong to detective and mystery stories genre?",
    "./data/charembench/data/book_level/genre-fiction.json":
        "Does character {character} belong to fiction genre?",
    "./data/charembench/data/book_level/genre-historical_fiction.json":
        "Does character {character} belong to historical fiction genre?",
    "./data/charembench/data/book_level/genre-humorous_stories.json":
        "Does character {character} belong to humorous stories genre?",
    "./data/charembench/data/book_level/genre-juvenile_fiction.json":
        "Does character {character} belong to juvenile fiction genre?",
    "./data/charembench/data/book_level/genre-love_stories.json":
        "Does character {character} belong to love stories genre?",
    "./data/charembench/data/book_level/genre-science_fiction.json":
        "Does character {character} belong to science fiction genre?",
    "./data/charembench/data/book_level/genre-short_stories.json":
        "Does character {character} belong to short stories genre?",
    "./data/charembench/data/book_level/genre-western_stories.json":
        "Does character {character} belong to western stories genre?",
}

output = "./data/charemberch-prepared"

# Create target directory if the latter does not exist.
if not exists(output):
    makedirs(output)

# reading char_map.
cbe_api = CEBApi()
cbe_api.read_char_map()

# reading pg-19 metadata.
pg19_api = PG19Api()
pg19_api.read("data/pg19/metadata.csv")

# reading char_map.
for fp, prompt in quiz_paths.items():
    with open(fp, "r") as input_file:

        # output filepath.
        ofp = join(output, basename(fp))
        with open(ofp, 'w') as output_file:

            content = json.load(input_file)
            for task in tqdm(content["data"]):
                speaker_id, answer = task
                book_id = speaker_id.split('_')[0]

                line = '\t'.join([
                    prompt.format(character=cbe_api.get_char_name(speaker_id)),
                    "Yes" if bool(answer) else "No"
                ])

                output_file.write("{}\n".format(line))
