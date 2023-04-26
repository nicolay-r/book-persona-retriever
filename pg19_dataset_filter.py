import json
import os
from os.path import join, basename
from tqdm import tqdm

#############################################################
# This script implements a filtering procedure.
# We consider to keep only such documents that
# presented in a list of the already processed documents.
# The result of filtering is copied in to a separated folder.
#############################################################

list_of_characters_path = "./data/charembench/data/chr_map.json"
pg_19_root_path = "./data/pg19"
pg_19_filtered_root_path = "./data/pg19-filtered"

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
books_to_be_keeped = []
for root, dir, files in os.walk(pg_19_root_path):
    print(root, dir, len(files))
    for f in files:
        if '.txt' not in f:
            continue
        complete_filepath = join(root, f)
        f_id = f.replace('.txt', '')
        if f_id in book_ids:
            books_to_be_keeped.append(complete_filepath)
        else:
            books_non_considered.append(complete_filepath)

print("---")
print("Total books:")
print(len(books_to_be_keeped) + len(books_non_considered))
print("Docs to be removed:")
print(len(books_to_be_keeped))

# Create target directory if the latter does not exist.
if not os.path.exists(pg_19_filtered_root_path):
    os.makedirs(pg_19_filtered_root_path)

# Copy the contents.
print("Copying files:")
for source_path in tqdm(books_to_be_keeped):
    target_path = join(pg_19_filtered_root_path, basename(source_path))
    copy_cmd = 'cp {} {}'.format(source_path, target_path)
    os.system(copy_cmd)
