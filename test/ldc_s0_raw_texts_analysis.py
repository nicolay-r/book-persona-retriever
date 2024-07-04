from os.path import join

from api.ceb import CEBApi
from utils import DATA_DIR


if __name__ == '__main__':

    # reading char_map
    ceb_api = CEBApi(books_root=join(DATA_DIR, "books"), char_map_path=join(DATA_DIR, "chr_map.json"))
    ceb_api.read_char_map()

    book_ids = ceb_api.book_ids_from_directory()
    books_count = len(book_ids)
    chars_count = ceb_api.characters_count(book_ids=book_ids)

    print("Books Considered: {}".format(books_count))
    print("Characters Count: {}".format(chars_count))
    print("Characters per book: {}".format(round(chars_count / books_count, 2)))