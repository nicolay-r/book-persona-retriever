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
                line = line.strip()
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

    @staticmethod
    def calc_annotated_dialogs_stat(iter_dialogs_and_speakers):
        recognized = 0
        dialogs = 0
        utterances = 0
        for dialog, recognized_speakers in tqdm(iter_dialogs_and_speakers):
            assert(isinstance(dialog, OrderedDict))

            for speaker_id in dialog.keys():
                assert(isinstance(recognized_speakers, dict))

                if speaker_id in recognized_speakers:
                    recognized += 1
                utterances += 1

            dialogs += 1

        return {
            "recognized": recognized,
            "utterances": utterances,
            "dialogs": dialogs
        }

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

    def write_lexicon(self, analysis_func, line_filter):
        assert(callable(analysis_func))

        result_sets = {}
        with open("{}-b{}.txt".format(self.prefixes_storage, self.books_count()), "w") as out:

            # We consider only positions 0, 1, 2, and 3
            # according to the related preliminary analysis.
            for k in tqdm([0, 1, 2, 3], desc="For each position of the character in comment"):
                tfa_idf = analysis_func(k=k, p_threshold=0.01,
                                        books_path_func=self.get_book_path,
                                        filter_func=lambda value: line_filter(value, result_sets))
                sorted_list = sorted(tfa_idf, key=lambda item: item[1], reverse=False)

                if k > 0:
                    for key, v in sorted_list:
                        out.write("{prefix}\n".format(prefix=key, value=round(v, 2)))

                result_sets[k] = set([k for k, _ in sorted_list])
