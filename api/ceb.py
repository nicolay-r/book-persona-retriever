import json
import os
from os.path import join

from core.book.paragraph import Paragraph
from core.utils import filter_whitespaces


class CEBApi:
    """ Character embedding benchmark API for Gutenberg books.
        Paper: https://aclanthology.org/2022.findings-acl.81/
        Github project: https://github.com/naoya-i/charembench
    """

    def __init__(self, books_root, char_map_path):
        """ Init API with the particular root provided for books and character mapping.
        """
        assert(isinstance(books_root, str))
        assert(isinstance(char_map_path, str))
        self.__book_storage_root = books_root
        self.__character_map_path = char_map_path
        self.__book_by_char = None
        self.__chars = None

    def _book_target(self, book_id):
        assert(isinstance(book_id, int))
        os.makedirs(self.__book_storage_root, exist_ok=True)
        return join(self.__book_storage_root, "{}.txt".format(str(book_id)))

    def save_book(self, book_id, text):
        """ Note: Used for annotated texts
        """
        assert (isinstance(text, str))
        target_filepath = self._book_target(book_id)
        with open(target_filepath, "w") as f:
            f.write(text)

    def check_book_exist(self, book_id):
        return os.path.exists(self._book_target(book_id))

    @staticmethod
    def is_speaker_id(value):
        if value.count("_") != 1:
            return False
        args = value.split("_")
        for p in args:
            if not p.isnumeric():
                return False
        return True

    @staticmethod
    def speaker_variant_to_speaker(speaker_variant, return_none=False):
        """ removes speaker variant from the complete speaker identifier.
            origin "BOOK_SID_VARIANT"
            returns: str
                of the following format: BOOK_SID
        """
        assert(isinstance(speaker_variant, str))
        assert("{" not in speaker_variant)
        assert("}" not in speaker_variant)

        if speaker_variant.count("_") != 2:
            if return_none:
                return None
            else:
                raise Exception("speaker name should include 2 underscore characters")

        book_id, speaker_id, _ = speaker_variant.split('_')
        return "{}_{}".format(book_id, speaker_id)

    @staticmethod
    def iter_book_paragraphs(text):
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
                yield paragraph
                paragraph = Paragraph(line_ind)
            else:
                paragraph.extend(line=line.strip('\n') + ' ', line_ind=line_ind)

        yield paragraph
        return

    @staticmethod
    def separate_character_entries(text):
        """ This method allow us demarcate literature characters from other words and punctuation signs.
        """
        assert(isinstance(text, str))
        text = text.replace("}", "} ").replace("{", " {")
        return " ".join(filter_whitespaces(text.split()))

    @staticmethod
    def iter_paragraphs(iter_book_ids, book_by_id_func):
        """ Iter paragraphs from the iter of books.
        """
        for book_id in iter_book_ids:
            with open(book_by_id_func(book_id), "r") as f:
                contents = f.read()
            for paragraph in CEBApi.iter_book_paragraphs(contents):
                yield paragraph

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

    def iter_chars(self):
        return self.__chars.keys()

    def get_char_names(self, char_id):
        """ List all the name variations for the particular book character.
        """
        assert(self.__chars is not None)
        return self.__chars[char_id]

    def characters_count(self, book_ids=None):
        if book_ids is None:
            # Consider characters from all books.
            return len(self.__book_by_char)

        total = 0
        for char_id in self.__book_by_char.keys():
            book_id = int(char_id.split('_')[0])
            total += 1 if book_id in book_ids else 0

        return total
