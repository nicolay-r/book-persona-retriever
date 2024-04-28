import sys
from os.path import join, exists

from tqdm import tqdm

from core.utils import download, create_dir_if_not_exist
from utils import DATA_DIR
from utils_ceb import CEBApi

sys.path.append('../')


if __name__ == '__main__':

    create_dir_if_not_exist(DATA_DIR)

    data = {
        join(DATA_DIR, "chr_map.json"): "https://raw.githubusercontent.com/naoya-i/charembench/main/data/chr_map.json",
        join(DATA_DIR, "pg19-metadata.txt"): "https://raw.githubusercontent.com/google-deepmind/pg19/master/metadata.csv",
    }

    for target, url in data.items():
        download(dest_file_path=target, source_url=url, desc=target)

    # Obtaining meta-data of the necessary books to download from Project Gutenberg
    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    ceb_api.read_char_map()
    ceb_books = ceb_api.book_ids_from_metadata()

    # Create directory for books.
    books_storage = join(DATA_DIR, "books/")
    create_dir_if_not_exist(books_storage)

    for book_id in tqdm(sorted(ceb_books), desc="Downloading books from Project Gutenberg"):
        target = join(books_storage, f"{book_id}.txt")
        if exists(target):
            continue
        download(source_url=f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
                 dest_file_path=target, desc=str(book_id), disable=True, silent=True)
