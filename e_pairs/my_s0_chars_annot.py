from collections import Counter
from os.path import join

from tqdm import tqdm
import sys

from utils import DATA_DIR

sys.path.append('../')

from utils_ceb import CEBApi
from utils_my import MyAPI

ctr = Counter()

# Source API.
source_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
source_api.read_char_map()

# Target API.
target_api = CEBApi(books_root=MyAPI.books_storage_en)

for book_id in tqdm(source_api.book_ids_from_directory(), desc="Annotating characters"):
    with open(source_api.get_book_path(book_id)) as f:
        book_text = f.read()
        for char_id in source_api.iter_book_chars(book_id):
            # Order characters by placing the long entries first.
            id_and_names = list(enumerate(source_api.get_char_names(char_id)))
            char_names = sorted(id_and_names, key=lambda item: len(item[1]), reverse=True)
            for name_id, name in char_names:
                html_annot_name = "{{{char_id}_{var_id}}}".format(char_id=char_id, var_id=name_id)
                ctr["missed" if name not in book_text else "found"] += 1
                book_text = book_text.replace(name, html_annot_name)

    target_api.save_book(book_id=book_id, text=book_text)

if ctr["found"] == 0:
    print(f"No books were found at: {MyAPI.books_storage_en}")
else:
    print("Found: {}%".format(round(ctr["found"] / (ctr["found"] + ctr["missed"]) * 100), 4))
