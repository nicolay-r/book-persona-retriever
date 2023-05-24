from collections import OrderedDict
from os import listdir
from os.path import join, dirname, realpath, isfile

from tqdm import tqdm


class MyAPI:
    """ Dataset developed for this particular studies
    """

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")
    prefixes_storage = join(__current_dir, "./data/ceb_books_annot/prefixes")
    dialogs_filepath = join(__current_dir, "./data/ceb_books_annot/dialogs.txt")  # dialogs storage.
    books_storage_en = join(books_storage, "en")

    def __init__(self, books_root=None):
        self.__book_storage_root = MyAPI.books_storage_en if books_root is None else books_root

    def get_book_path(self, book_id):
        return join(self.__book_storage_root, "{book_id}.txt".format(book_id=book_id))

    @staticmethod
    def load_prefix_lexicon_en(default_suffix="b500", filepath=None):
        """ Loading the aux lexicon which allow us recognize characters in text.
            default suffix is an amount of considered books.
        """
        entries = set()
        filepath = "{}-{}.txt".format(MyAPI.prefixes_storage, default_suffix) if filepath is None else filepath
        with open(filepath, "r") as f:
            for line in f.readlines():
                # split n-gramms.
                entries.add(line.replace('~', ' '))
        return entries

    def books_count(self):
        count = 0
        dir_path = self.__book_storage_root
        for path in listdir(dir_path):
            # check if current path is a file
            if isfile(join(dir_path, path)):
                count += 1
        return count

    def write_annotated_dialogs(self, iter_dialogs_and_speakers, filepath=None, print_sep=True):
        filepath = self.dialogs_filepath if filepath is None else filepath

        with open(filepath, "w") as file:
            for dialog, recognized_speakers in tqdm(iter_dialogs_and_speakers):
                assert(isinstance(dialog, OrderedDict))

                for speaker_id, segments in dialog.items():
                    assert(isinstance(segments, list))
                    assert(isinstance(recognized_speakers, dict))

                    sep = " " if print_sep is False else " [USEP] "
                    utterance = sep.join(segments)
                    speaker = recognized_speakers[speaker_id] \
                        if speaker_id in recognized_speakers else "UNKN-{}".format(speaker_id)
                    file.write("{speaker}: {utterance}\n".format(speaker=speaker, utterance=utterance))

                file.write('\n')
