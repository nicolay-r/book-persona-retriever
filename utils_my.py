import os
from collections import OrderedDict, Counter
from os import listdir
from os.path import join, dirname, realpath, isfile

from tqdm import tqdm

from core.book_dialog import BookDialogueService
from utils import range_exclude_middle, range_middle


class MyAPI:
    """ Dataset developed for this particular studies
    """

    # Setup parameters for the dataset generation
    response_persona_prefix = ""
    candidates_shuffle_seed = 42
    dataset_min_utterances_per_char = 100
    dataset_max_utterances_per_char = 100
    dataset_folding_parts = 10
    dataset_train_parts = range_exclude_middle(dataset_folding_parts)
    dataset_valid_parts = range_middle(dataset_folding_parts)
    dataset_candidates_limit = 20
    traits_per_character = 8

    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")
    prefixes_storage = join(__current_dir, "./data/ceb_books_annot/prefixes")
    # Dialogs with recognized speakers.
    dialogs_filepath = join(__current_dir, "./data/ceb_books_annot/dialogs.txt")
    # List of the speakers considered for the dataset.
    filtered_speakers_filepath = join(__current_dir, "./data/ceb_books_annot/filtered_speakers.txt")
    dataset_filepath = join(__current_dir, "./data/ceb_books_annot/dataset.txt")
    dataset_fold_filepath = join(__current_dir, "./data/ceb_books_annot/dataset_f{fold_index}.txt")
    dataset_parlai_filepath = join(__current_dir, "./data/ceb_books_annot/dataset_parlai_{}.zip")
    # Embedding visualization for queries in dataset (original texts.
    dataset_st_embedding_query = join(__current_dir, "./data/ceb_books_annot/x.dataset-query-sent-transformers.npz")
    dataset_st_embedding_response = join(__current_dir, "./data/ceb_books_annot/x.dataset-response-sent-transformers.txt")
    books_storage_en = join(books_storage, "en")
    # spectrums-related data
    spectrum_features = join(__current_dir, "./data/ceb_books_annot/x.spectrum-embeddings.npz")
    spectrum_speakers = join(__current_dir, "./data/ceb_books_annot/y.spectrum-speakers.npz")
    spectrum_default_preset = "prompt_most_imported_limited_{}".format(str(traits_per_character))
    spectrum_st_embeddings = join(__current_dir, "./data/ceb_books_annot/x.spectrum-embeddings-sent-transformers-{preset}.npz")
    # intermediate file required for a quick embedding of traits into the
    # train/validation dataset for dialogue chatbot development.
    spectrum_prompts_filepath = join(__current_dir,
                                     "./data/ceb_books_annot/spectrum_speaker_prompts-{preset}.txt".format(
                                         preset=spectrum_default_preset))

    # separator in line between meta information and the actual content
    meta_sep = ": "

    unknown_speaker = "UNKN-"

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

                    sep = " " if print_sep is False else " {} ".format(BookDialogueService.utterance_sep)
                    utterance = sep.join(segments)
                    speaker = recognized_speakers[speaker_id] \
                        if speaker_id in recognized_speakers else MyAPI.unknown_speaker+str(speaker_id)
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

    @staticmethod
    def _get_meta(line):
        return line.split(MyAPI.meta_sep)[0]

    @staticmethod
    def write_dataset_buffer(file, buffer):
        assert(isinstance(buffer, list) and len(buffer) == 2)
        for buffer_line in buffer:
            file.write("{}\n".format(buffer_line))
        file.write("\n")

    def write_dataset(self, buffer_filter_func=None):
        """ Filter dialogs to the result dataset. Compose a Question->Response pair.
            Where response is always a known speaker, so whe know who we ask.
        """
        assert(callable(buffer_filter_func) or buffer_filter_func is None)

        # Read speakers to be considered first.
        speakers_set = set(self.read_speakers())

        buffer = []
        counter = Counter()
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

                speaker_name = MyAPI._get_meta(line)

                # We optionally filter buffers first.
                if buffer_filter_func is not None:
                    if not buffer_filter_func(speaker_name, buffer):
                        continue

                # We consider only such speakers that in predefined list.
                # We know we have a response to the known speaker.
                if MyAPI.unknown_speaker not in speaker_name and speaker_name in speakers_set:
                    # We release content from the buffer.
                    MyAPI.write_dataset_buffer(file=file, buffer=buffer)
                    counter["pairs"] += 1

        print("Pairs written: {}".format(counter["pairs"]))
        print("Dataset saved: {}".format(self.dataset_filepath))

    @staticmethod
    def read_dataset(dataset_filepath, keep_usep=True, split_meta=False, desc=None, pbar=True):
        """ split_meta: bool
                whether we want to split in parts that before ":"
        """
        assert(isinstance(dataset_filepath, str))

        with open(dataset_filepath, "r") as file:
            for line in tqdm(file.readlines(), desc=desc, disable=not pbar):

                if not keep_usep:
                    # Remove this.
                    line = line.replace(BookDialogueService.utterance_sep, "")

                line = line.strip() if line != "\n" else None

                if line is None:
                    yield None
                    continue

                if split_meta:
                    # Separate meta information from the line.
                    meta = MyAPI._get_meta(line)
                    text = line[len(meta) + len(MyAPI.meta_sep):]
                    yield meta, text
                else:
                    yield line

    @staticmethod
    def check_speakers_count(dataset_filepath, pbar=True):
        """ Folding with the even splits of the utterances.
        """
        partners_count = Counter()

        utt = []

        args_it = MyAPI.read_dataset(
            keep_usep=False, split_meta=True, dataset_filepath=dataset_filepath, pbar=pbar)

        for args in args_it:

            if args is None:
                utt.clear()
                continue

            s_name, _ = args

            utt.append(s_name)

            # response of the partner.
            if len(utt) == 2:
                # Count the amount of partners.
                partners_count[s_name] += 1

        return partners_count

    def save_speaker_spectrums(self, speaker_names, speaker_prompts):
        with open(self.spectrum_prompts_filepath,  "w") as file:
            for i, p in enumerate(speaker_prompts):
                line = "".join([speaker_names[i], MyAPI.meta_sep, ",".join(p.split(' '))])
                file.write(line + "\n")

    def read_speaker_spectrums(self):
        with open(self.spectrum_prompts_filepath, "r") as file:
            spectrums = {}
            for line in file.readlines():
                speaker_name, args = line.split(MyAPI.meta_sep)
                spectrums[speaker_name] = [a.strip() for a in args.split(',')]

        return spectrums
