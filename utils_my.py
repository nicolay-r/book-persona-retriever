from os import listdir
from os.path import join, dirname, realpath, isfile


class MyAPI:
    """ Dataset developed for this particular studies
    """

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")
    books_storage_en = join(books_storage, "en")

    def __init__(self, books_root=None):
        self.__book_storage_root = MyAPI.books_storage_en if books_root is None else books_root

    def get_book_path(self, book_id):
        return join(self.__book_storage_root, "{book_id}.txt".format(book_id=book_id))

    def books_count(self):
        count = 0
        dir_path = self.__book_storage_root
        for path in listdir(dir_path):
            # check if current path is a file
            if isfile(join(dir_path, path)):
                count += 1
        return count
