import argparse

from tqdm import tqdm
from os.path import join
from collections import Counter

from api.ceb import CEBApi
from api.my import MyAPI
from utils import DATA_DIR

import sys
sys.path.append('../')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-no-skip', dest='no_skip_existed', default="false", action="store_true")

    args = parser.parse_args()

    # Source API.
    source_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    source_api.read_char_map()

    # Target API.
    target_api = CEBApi(books_root=MyAPI.books_storage_en, char_map_path=join(DATA_DIR, "chr_map.json"))

    ctr = Counter()
    for book_id in tqdm(source_api.book_ids_from_directory(), desc="Annotating characters", unit="book"):

        # Skip those books that were already processed.
        if target_api.check_book_exist(book_id) and args.no_skip_existed:
            continue

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
