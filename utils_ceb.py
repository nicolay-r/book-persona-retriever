import json
import os
from os.path import dirname, realpath, join


class CEBApi:
    """ Character embedding benchmark API
    """

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_test")
    books_storage_en = join(__current_dir, books_storage, "./en")
    character_map = join(__current_dir, "./data/charembench/data/chr_map.json")

    def __init__(self):
        self.__book_by_char = None
        self.__chars = None

    def read(self, path=None):
        """ reading char_map
        """
        path = path if path is not None else self.character_map
        self.__book_by_char = {}
        with open(path, "r") as f:
            self.__chars = json.load(f)
            for char_id in self.__chars.keys():
                book_id = char_id.split('_')[0]
                self.__book_by_char[char_id] = book_id

    def book_ids_from_metadata(self):
        books_ids = set()
        for char_id in self.__chars.keys():
            books_ids.add(int(self.__book_by_char[char_id]))
        return books_ids

    def book_ids_from_directory(self):
        """ Files are named XXX.txt, where XXX is an index of integer type
        """
        books_ids = set()
        for _, _, files in os.walk(self.books_storage_en):
            for f in files:
                upd_name = f.replace('.txt', '')
                books_ids.add(int(upd_name))

        return books_ids

    def __get_char_name(self, char_id, try_index=0):
        """ ind: int
                there might be many variations of how characters are mentioned,
                so we can select via 'ind' parameter.
        """
        names = self.__chars[char_id]
        try_index = try_index % len(names)
        return names[try_index]

    def replace_characters_in_text(self, text):
        terms = [t.strip() for t in text.split()]
        for i in range(len(terms)):
            if terms[i] not in self.__chars:
                continue

            # replace it with the related name
            terms[i] = self.__get_char_name(terms[i])

        return ' '.join(terms)

    def get_char_name(self, char_id, try_index=0):
        return self.__get_char_name(char_id=char_id, try_index=try_index)
