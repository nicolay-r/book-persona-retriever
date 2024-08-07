import os
from collections import OrderedDict, Counter
from os import listdir
from os.path import join, isfile

from tqdm import tqdm

from api.utils import range_exclude_middle, range_middle
from core.book.book_dialog import BookDialogue
from core.utils import count_files_in_folder
from utils import DATA_DIR


class LdcAPI:
    """ Literature Dialogue Dataset (LDC) API
    """

    # Main parameters.
    books_storage = join(DATA_DIR, "books_annot")
    books_storage_en = join(books_storage, "en")

    # Prefixes lexicon storage configurations.
    prefixes_storage_filepath = join(books_storage, "./prefixes.txt")
    # Dialogs with recognized speakers.
    dialogs_recongize_speaker_p_threshold = 0.01
    dialogs_recognize_speaker_at_positions = [0, 1, 2, 3]  # We consider only positions 0, 1, 2, and 3
                                                           # according to the related preliminary analysis.
    dialogs_filepath = join(books_storage, "./dialogs.txt")
    # Setup parameters for the dataset generation
    filtered_speakers_filepath = join(books_storage, "./filtered_speakers.txt")
    # Speakers filtering parameters.
    dataset_min_words_count_in_response = 10
    dataset_filter_speaker_total_speakers_count = 400
    dataset_predefined_speakers_count = 100
    dataset_filter_speaker_min_utterances_per_speaker = None
    dataset_filter_other_speakers_in_response = 0
    dataset_filepath = join(books_storage, "./dataset.txt")
    dataset_fold_filepath = join(books_storage, "./dataset_f{fold_index}.txt")
    dataset_filter_dialogue_max_utterances_per_speaker = 100
    # Dataset folding.
    dataset_folding_parts = 5
    dataset_folding_fixed_parts = {
        'train': range_exclude_middle(dataset_folding_parts),
        "valid": range_middle(dataset_folding_parts),
    }
    dataset_st_embedding_query = join(books_storage, "./x.dataset-query-sent-transformers.npz")
    dataset_st_embedding_response = join(books_storage, "./x.dataset-response-sent-transformers.txt")
    dataset_dialog_db_path = join(books_storage, "./dataset_dialog.sqlite")
    dataset_dialog_db_fold_path = join(books_storage, "./dataset_dialog_{fold_index}.sqlite")

    # ParlAI dataset creation related parameters.
    parlai_dataset_candidates_limit = 20
    parlai_dataset_persona_prefix = ""
    parlai_dataset_episode_candidates_and_traits_shuffle_seed = 42
    parlai_dataset_ovesampling_candidates_selection_seed = 42
    parlai_dataset_filepath = join(books_storage, "./dataset_parlai_{}.zip")
    parlai_charmask_template = "_"      # We perform character masking for the ParlAI dataset of utterances.
    parlai_dataset_train_candidates_oversample_factor = 5   # In ALOHA paper, authors end up dealing with 1M dialogue lines.
                                                            # For the similar amount of speakers in books, we deal with ~40K
                                                            # lines by default. Hence we introduce oversampling for
                                                            # candidate-selective approach to get closer to experiments in
                                                            # ALOHA paper.

    # 507_9. Bartle Massey -- The schoolteacher and Adam’s best friend. Unbeknownst to his friends, not only does Mr. Massey care deeply for his students, but he exhibits a patience with them that he seldom shows in the company of friends. Mr. Massey rails against the stupidity of women and says everything twice. During Hetty’s trial, he is a tactful comfort to Adam because he is able to see when it is best not to speak.I
    # 139_1 The Lost World by Arthur Conan Doyle ['Summerlee', 'Mr. Summerlee', 'SUMMERLEE'] UNK https://arthurconandoyle.co.uk/character/professor-summerlee-from-the-professor-challenger-stories
    # 1257_9 The Three Musketeers by Alexandre Dumas Pere ['Buckingham', 'Duke', 'Lord Duke', 'Lord Buckingham', 'Duke of Buckingham'] https://heroes-and-villain.fandom.com/wiki/Duke_of_Buckingham_(2011)
    # 155_21 The Moonstone by Wilkie Collins ['Sergeant', 'Mr. Cuff', 'Sergeant Cuff'] UNK https://www.litcharts.com/lit/the-moonstone/characters/sergeant-cuff#:~:text=A%20%E2%80%9Crenowned%20and%20capable%E2%80%9D%20detective,%2C%20Franklin%20Blake%2C%20and%20Mr.
    # 507_3 Soldiers of Fortune by Richard Harding Davis ['MacWilliams', 'Mr. MacWilliams'] https://www.theatlantic.com/magazine/archive/1897/12/mr-daviss-soldiers-of-fortune/636194/
    predefined_speakers = ['507_3', '139_1', '1257_9', '155_21', '403_3']

    # separator in line between meta information and the actual content
    meta_sep = ": "
    dialogs_unknown_speaker = "UNKN-"

    def __init__(self, books_root=None):
        self.__book_storage_root = LdcAPI.books_storage_en if books_root is None else books_root

    def get_book_path(self, book_id):
        return join(self.__book_storage_root, "{book_id}.txt".format(book_id=book_id))

    def get_total_books(self):
        return count_files_in_folder(self.__book_storage_root)

    def books_count(self):
        count = 0
        dir_path = self.__book_storage_root
        for path in listdir(dir_path):
            # check if current path is a file
            if isfile(join(dir_path, path)):
                count += 1
        return count

    def book_ids_from_directory(self):
        """ Files are named XXX.txt, where XXX is an index of integer type
        """
        books_ids = set()
        for _, _, files in os.walk(self.__book_storage_root):
            for f in files:
                upd_name = f.replace('.txt', '')
                books_ids.add(int(upd_name))

        return books_ids

    @staticmethod
    def utterance_to_str(speaker_id, utterance):
        return "{speaker}: {utterance}".format(speaker=speaker_id, utterance=utterance)

    @staticmethod
    def write_annotated_dialogs(iter_dialogs_and_speakers, filepath=None, print_sep=True):
        filepath = LdcAPI.dialogs_filepath if filepath is None else filepath

        with open(filepath, "w") as file:
            for dialog, recognized_speakers in iter_dialogs_and_speakers:
                assert(isinstance(dialog, OrderedDict))

                for speaker_id, segments in dialog.items():
                    assert(isinstance(segments, list))
                    assert(isinstance(recognized_speakers, dict))

                    sep = " " if print_sep is False else " {} ".format(BookDialogue.utterance_sep)
                    utterance = sep.join(segments)
                    speaker = recognized_speakers[speaker_id] \
                        if speaker_id in recognized_speakers else LdcAPI.dialogs_unknown_speaker + str(speaker_id)

                    line = LdcAPI.utterance_to_str(speaker_id=speaker, utterance=utterance)

                    file.write("{}\n".format(line))

                file.write('\n')

    @staticmethod
    def _read_annotated_dialogs(filepath=None, desc=None):
        with open(filepath, "r") as file:
            for line in tqdm(file.readlines(), desc=desc):
                if line == "\n":
                    # End of the dialog.
                    yield None
                else:
                    yield line

    @staticmethod
    def load_prefix_lexicon_en(filepath=None):
        """ Loading the aux lexicon which allow us recognize characters in text.
            default suffix is an amount of considered books.
        """
        entries = set()

        with open(LdcAPI.prefixes_storage_filepath if filepath is None else filepath, "r") as f:
            for line in f.readlines():
                # split n-gramms.
                line = line.strip()
                entries.add(line.replace('~', ' '))

        return entries

    def write_lexicon(self, rows_iter):
        with open(LdcAPI.prefixes_storage_filepath, "w") as f_out:
            for row in rows_iter:
                f_out.write("{}\n".format(row))

    @staticmethod
    def write_speakers(speaker_names_list, filepath=None):
        assert(isinstance(speaker_names_list, list))

        filepath = LdcAPI.filtered_speakers_filepath if filepath is None else filepath

        with open(filepath, "w") as f:
            for speaker_name in speaker_names_list:
                f.write("{}\n".format(speaker_name))

        print(f"Speakers saved: {filepath}")

    @staticmethod
    def read_speakers(filepath=None):
        assert(isinstance(filepath, str) or filepath is None)

        filepath = LdcAPI.filtered_speakers_filepath if filepath is None else filepath

        speakers = []
        with open(filepath, "r") as f:
            for line in f.readlines():
                speakers.append(line.strip())

        return speakers

    @staticmethod
    def _get_meta(line):
        return line.split(LdcAPI.meta_sep)[0]

    @staticmethod
    def _get_utterance_or_empty(line):
        args = line.split(LdcAPI.meta_sep)
        return args[1] if len(args) > 1 else ""

    @staticmethod
    def write_dataset_buffer(file, buffer):
        assert(isinstance(buffer, list) and len(buffer) == 2)
        for buffer_line in buffer:
            assert(isinstance(buffer_line, tuple) or isinstance(buffer_line, str))

            if isinstance(buffer_line, tuple):
                assert(len(buffer_line) == 2)
                buffer_line = LdcAPI.utterance_to_str(speaker_id=buffer_line[0], utterance=buffer_line[1])

            file.write("{}\n".format(buffer_line))
        file.write("\n")

    @staticmethod
    def iter_dialog_question_response_pairs(dialogs_filepath, dialogue_filter_func=None, desc=None):
        """ dialogue_filter_func: func (speaker_name, dialogue)
                serves as a filtering function for a dialogue and a response speaker name.
        """

        qr_utterance_pair = []
        for line in LdcAPI._read_annotated_dialogs(filepath=dialogs_filepath, desc=desc):

            if line is None:
                continue

            line = line.strip()
            qr_utterance_pair.append(LdcAPI._get_utterance_or_empty(line))

            # Keep the size of buffer equal 2.
            if len(qr_utterance_pair) > 2:
                qr_utterance_pair = qr_utterance_pair[1:]

            if len(qr_utterance_pair) != 2:
                continue

            # Parse speaker name.
            r_speaker_id = LdcAPI._get_meta(line)

            # We consider None in the case when the responding speaker is unknown.
            r_speaker_id = None if LdcAPI.dialogs_unknown_speaker in r_speaker_id else r_speaker_id

            # We optionally filter buffers first.
            if dialogue_filter_func is not None:
                if not dialogue_filter_func(r_speaker_id, qr_utterance_pair):
                    continue

            yield r_speaker_id, qr_utterance_pair

    @staticmethod
    def write_dataset(dialog_qr_pairs_iter, speakers_set=None, filepath=None):
        assert(isinstance(speakers_set, set) or speakers_set is None)

        filepath = LdcAPI.dataset_filepath if filepath is None else filepath

        counter = Counter()
        with open(filepath, "w") as file:
            for r_speaker_id, qr_utterance_pair in dialog_qr_pairs_iter:
                assert(len(qr_utterance_pair) == 2)

                # We do not consider `r_speaker_id` with the None value.
                if r_speaker_id is None:
                    continue

                # We consider only such speakers that in speakers_set (optional).
                if speakers_set is not None:
                    if r_speaker_id not in speakers_set:
                        continue

                # We combine lines with the speaker information as it was before.
                buffer = [None] * 2
                buffer[0] = LdcAPI.dialogs_unknown_speaker + "X" + LdcAPI.meta_sep + qr_utterance_pair[0]
                buffer[1] = r_speaker_id + LdcAPI.meta_sep + qr_utterance_pair[1]

                LdcAPI.write_dataset_buffer(file=file, buffer=buffer)
                counter["pairs"] += 1

        print("Pairs written: {}".format(counter["pairs"]))
        print("Dataset saved: {}".format(filepath))

    @staticmethod
    def read_dataset(dataset_filepath, keep_usep=True, split_meta=False, desc=None, pbar=True, limit=None):
        """ split_meta: bool
                whether we want to split in parts that before ":"
        """
        assert(isinstance(dataset_filepath, str))

        c = Counter()
        c["lines_total"] = 0

        with open(dataset_filepath, "r") as file:
            for line in tqdm(file.readlines(), desc=desc, disable=not pbar):

                c["lines_total"] += 1
                if limit is not None and c["lines_total"] > limit:
                    break

                if not keep_usep:
                    # Remove this.
                    line = line.replace(BookDialogue.utterance_sep, "")

                line = line.strip() if line != "\n" else None

                if line is None:
                    yield None
                    continue

                if split_meta:
                    # Separate meta information from the line.
                    meta = LdcAPI._get_meta(line)
                    text = line[len(meta) + len(LdcAPI.meta_sep):]
                    yield meta, text
                else:
                    yield line

    @staticmethod
    def iter_dataset_as_dialogs(dataset_lines_iter):
        """ This method allows to read the dataset in a form of the
            question-response, i.e. "dialogs". It yields dialog lines in output.
        """

        lines = []
        for line in dataset_lines_iter:
            # End of the dialog

            if line is None:
                lines.clear()
                continue

            lines.append(line)

            if len(lines) < 2:
                continue

            yield lines
            lines.clear()

    @staticmethod
    def calc_utterances_per_speakers_count(dataset_filepath, pbar=True):
        """ Folding with the even splits of the utterances.
        """

        dialogs_it = LdcAPI.iter_dataset_as_dialogs(
            LdcAPI.read_dataset(keep_usep=False, split_meta=True,
                                dataset_filepath=dataset_filepath, pbar=pbar))

        partners_count = Counter()
        for dialog in dialogs_it:
            partner_id = dialog[1][0]
            partners_count[partner_id] += 1

        return partners_count
