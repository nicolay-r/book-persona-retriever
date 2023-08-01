import os
import json
from utils_ceb import CEBApi
from utils_pg19 import PG19Api
from os.path import join, basename
from tqdm import tqdm

#############################################################
# This script implements a filtering procedure.
# We consider to keep only such documents that
# presented in a list of the already processed documents.
# The result of filtering is copied in to a separated folder.
#############################################################

source_path = PG19Api.books_storage
target_path = CEBApi.books_storage_en
list_of_characters_path = CEBApi.character_map

book_ids = set()

# reading char_map
with open(list_of_characters_path, "r") as f:
    chars = json.load(f)
    for k in chars.keys():
        book_id = k.split('_')[0]
        book_ids.add(book_id)

print('---')
print("Total documents count:")
print(len(book_ids))
books_non_considered = []
books_to_be_kept = []
for root, dir, files in os.walk(source_path):
    print(root, dir, len(files))
    for f in files:
        if '.txt' not in f:
            continue
        complete_filepath = join(root, f)
        f_id = f.replace('.txt', '')
        if f_id in book_ids:
            books_to_be_kept.append(complete_filepath)
        else:
            books_non_considered.append(complete_filepath)

print("---")
print("Total books:")
print(len(books_to_be_kept) + len(books_non_considered))
print("Docs to be removed:")
print(len(books_to_be_kept))

# Create target directory if the latter does not exist.
if not os.path.exists(target_path):
    os.makedirs(target_path)

# Copy the contents.
print("Copying files:")
for source_path in tqdm(books_to_be_kept):
    copy_cmd = 'cp {} {}'.format(source_path, join(target_path, basename(source_path)))
    os.system(copy_cmd)
