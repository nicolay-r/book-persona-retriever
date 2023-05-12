import json
import os
from os.path import dirname, realpath, join

from utils import Paragraph


class CEBApi:
    """ Character embedding benchmark API for Gutenberg books.
        Paper: https://aclanthology.org/2022.findings-acl.81/
        Github project: https://github.com/naoya-i/charembench
    """

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books")
    books_storage_en = join(__current_dir, books_storage, "./en")
    character_map = join(__current_dir, "./data/charembench/data/chr_map.json")

    def __init__(self, books_root=None, char_map_path=None):
        """ Init API with the particular root provided for books and character mapping.
        """
        assert(isinstance(books_root, str) or books_root is None)
        assert(isinstance(char_map_path, str) or char_map_path is None)
        self.__book_storage_root = CEBApi.books_storage_en if books_root is None else books_root
        self.__character_map_path = CEBApi.character_map if char_map_path is None else char_map_path
        self.__book_by_char = None
        self.__chars = None

    def save_book(self, book_id, text):
        """ Note: Used for annotated texts
        """
        assert(isinstance(book_id, int))
        assert(isinstance(text, str))

        os.makedirs(self.__book_storage_root, exist_ok=True)

        target_filepath = join(self.__book_storage_root, "{}.txt".format(str(book_id)))
        with open(target_filepath, "w") as f:
            f.write(text)

    def iter_book_paragraphs(self, text):
        """ paragraphs extraction from `text`
            proposed by following project:
            https://github.com/ricsinaruto/gutenberg-dialog
        """
        assert(isinstance(text, str))
        paragraph = Paragraph(0)
        for line_ind, line in enumerate(text.split('\n')):
            # Paragraphs are separated by new line.
            # Usually one paragraph contains a single speaker.
            if len(line.strip()) == 0:
                yield paragraph.Text
                paragraph = Paragraph(line_ind)
            else:
                paragraph.extend(line=line.strip('\n') + ' ', line_ind=line_ind)

        yield " "
        return

    def read_char_map(self):
        """ reading char_map, which has been composed by.
            https://aclanthology.org/D15-1088.pdf
        """
        self.__book_by_char = {}
        with open(self.__character_map_path, "r") as f:
            self.__chars = json.load(f)
            for char_id in self.__chars.keys():
                book_id = char_id.split('_')[0]
                self.__book_by_char[char_id] = book_id

    def get_book_path(self, book_id):
        return join(self.__book_storage_root, "{book_id}.txt".format(book_id=book_id))

    def book_ids_from_metadata(self):
        books_ids = set()
        for char_id in self.__chars.keys():
            books_ids.add(int(self.__book_by_char[char_id]))
        return books_ids

    def book_ids_from_directory(self):
        """ Files are named XXX.txt, where XXX is an index of integer type
        """
        books_ids = set()
        for _, _, files in os.walk(self.__book_storage_root):
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

    def iter_book_chars(self, book_id):
        for char_id in self.__chars.keys():
            assert(isinstance(char_id, str))
            if char_id.startswith(str(book_id) + "_"):
                yield char_id

    def get_char_names(self, char_id):
        """ List all the name variations for the particular book character.
        """
        return self.__chars[char_id]
