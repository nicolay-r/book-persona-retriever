from collections import OrderedDict, Counter
from os import listdir
from os.path import join, dirname, realpath, isfile

from tqdm import tqdm


class MyAPI:
    """ Dataset developed for this particular studies
    """

    min_utterances_per_char = 5
    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")
    prefixes_storage = join(__current_dir, "./data/ceb_books_annot/prefixes")
    # Dialogs with recognized speakers.
    dialogs_filepath = join(__current_dir, "./data/ceb_books_annot/dialogs.txt")
    # List of the speakers considered for the dataset.
    filtered_speakers_filepath = join(__current_dir, "./data/ceb_books_annot/filtered_speakers.txt")
    dataset_filepath = join(__current_dir, "./data/ceb_books_annot/dataset.txt")
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

    @staticmethod
    def calc_annotated_dialogs_stat(iter_dialogs_and_speakers):
        """ iter_dialog_and_speakers: iter
                iter of data (dialog, recognized_speakers), where
                    recognized_speakers (dict): {speaker_id: speaker}
                        speaker_id: BOOK_SPEAKER_VAR,
                        speaker: BOOK_SPEAKER.
        """
        dialogs = 0
        recognized = 0
        utterances = 0
        speaker_utts_stat = Counter()       # Per every utterance
        speaker_reply_stat = Counter()      # Per replies
        it = tqdm(iter_dialogs_and_speakers, desc="calculating annotated dialogues stat")
        for dialog, recognized_speakers in it:
            assert(isinstance(dialog, OrderedDict))

            for utt_index, speaker_id in enumerate(dialog.keys()):
                assert(isinstance(recognized_speakers, dict))

                if speaker_id in recognized_speakers:
                    recognized += 1

                    # register speaker
                    speaker = recognized_speakers[speaker_id]
                    speaker_utts_stat[speaker] += 1

                    if utt_index > 0:
                        speaker_reply_stat[speaker] += 1

                utterances += 1

            dialogs += 1

        return {
            "recognized": recognized,
            "utterances": utterances,
            "dialogs": dialogs,
            "speakers_uc_stat": speaker_utts_stat,
            "speakers_reply_stat": speaker_reply_stat,
        }

    def write_annotated_dialogs(self, iter_dialogs_and_speakers, filepath=None, print_sep=True):
        filepath = self.dialogs_filepath if filepath is None else filepath

        with open(filepath, "w") as file:
            it = tqdm(iter_dialogs_and_speakers, desc="writing dialogues")
            for dialog, recognized_speakers in it:
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

    def read_annotated_dialogs(self, filepath=None):
        filepath = self.dialogs_filepath if filepath is None else filepath

        with open(filepath, "r") as file:
            for line in tqdm(file.readlines(), desc="handle annotated utterances"):
                if line == "\n":
                    # End of the dialog.
                    yield None
                else:
                    yield line

    def load_prefix_lexicon_en(self):
        """ Loading the aux lexicon which allow us recognize characters in text.
            default suffix is an amount of considered books.
        """
        entries = set()
        with open("{}-b{}.txt".format(self.prefixes_storage, self.books_count()), "r") as f:
            for line in f.readlines():
                # split n-gramms.
                line = line.strip()
                entries.add(line.replace('~', ' '))
        return entries

    def write_lexicon(self, analysis_func, line_filter):
        assert(callable(analysis_func))

        result_sets = {}
        with open("{}-b{}.txt".format(self.prefixes_storage, self.books_count()), "w") as out:

            # We consider only positions 0, 1, 2, and 3
            # according to the related preliminary analysis.
            for k in tqdm([0, 1, 2, 3], desc="For each position of the character in comment"):
                tfa_idf = analysis_func(k=k, p_threshold=0.01 if k > 1 else None,
                                        books_path_func=self.get_book_path,
                                        filter_func=lambda value: line_filter(value, result_sets))
                sorted_list = sorted(tfa_idf, key=lambda item: item[1], reverse=False)

                if k > 0:
                    for key, v in sorted_list:
                        out.write("{prefix}\n".format(prefix=key, value=round(v, 2)))

                result_sets[k] = set([k for k, _ in sorted_list])

    def write_speakers(self, speaker_names_list):
        assert(isinstance(speaker_names_list, list))
        with open(self.filtered_speakers_filepath, "w") as f:
            for speaker_name in speaker_names_list:
                f.write("{}\n".format(speaker_name))

    def read_speakers(self):
        speakers = []
        with open(self.filtered_speakers_filepath, "r") as f:
            for line in f.readlines():
                speakers.append(line.strip())
        return speakers

    def compose_dataset(self):
        """ Filter dialogs to the result dataset. Compose a Question->Response pair.
            Where response is always a known speaker, so whe know who we ask.
        """

        # Read speakers to be considered first.
        speakers_set = set()
        with open(self.filtered_speakers_filepath, "r") as f:
            for speaker_name in f.readlines():
                speakers_set.add(speaker_name.strip())

        pairs = 0
        buffer = []
        with open(self.dataset_filepath, "w") as file:
            for line in self.read_annotated_dialogs():
                if line is None:
                    continue
                line = line.strip()
                buffer.append(line)

                # Keep the size of buffer equal 2.
                if len(buffer) > 2:
                    buffer = buffer[1:]

                if len(buffer) != 2:
                    continue

                speaker_name = line.split(': ')[0]

                # We consider only such speakers that in predefined list.
                # We know we have a response to the known speaker.
                if "UNKN" not in speaker_name and speaker_name in speakers_set:
                    # We release content from the buffer.
                    for buffer_line in buffer:
                        file.write("{}\n".format(buffer_line))
                    file.write("\n")
                    pairs += 1

        print("Pairs written: {}".format(pairs))
        print("Dataset saved: {}".format(self.dataset_filepath))

    def read_dataset(self):
        with open(self.dataset_filepath, "r") as file:
            for line in tqdm(file.readlines()):
                yield line if line != "\n" else None
