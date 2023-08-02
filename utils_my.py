import os
from collections import OrderedDict, Counter
from os import listdir
from os.path import join, dirname, realpath, isfile

from tqdm import tqdm

from core.book.book_dialog import BookDialogue
from embeddings.aloha.cfg import MatrixTrainingConfig, ClusterConfig
from utils import range_exclude_middle, range_middle


class MyAPI:
    """ Dataset developed for this particular studies
    """

    # Main parameters.
    __current_dir = dirname(realpath(__file__))
    books_storage = join(__current_dir, "./data/ceb_books_annot")
    books_storage_en = join(books_storage, "en")

    # Prefixes lexicon storage configurations.
    prefixes_storage = join(__current_dir, "./data/ceb_books_annot/prefixes")
    # Dialogs with recognized speakers.
    dialogs_filepath = join(__current_dir, "./data/ceb_books_annot/dialogs.txt")
    # Setup parameters for the dataset generation
    filtered_speakers_filepath = join(__current_dir, "./data/ceb_books_annot/filtered_speakers.txt")
    # Speakers filtering parameters.
    dataset_min_words_count_in_response = 10
    dataset_filter_speaker_total_speakers_count = 400
    dataset_filter_speaker_min_utterances_per_char = None
    dataset_filepath = join(__current_dir, "./data/ceb_books_annot/dataset.txt")
    dataset_fold_filepath = join(__current_dir, "./data/ceb_books_annot/dataset_f{fold_index}.txt")
    dataset_filter_dialogue_max_utterances_per_char = 100
    dataset_folding_parts = 5
    dataset_train_parts = range_exclude_middle(dataset_folding_parts)
    dataset_valid_parts = range_middle(dataset_folding_parts)
    dataset_st_embedding_query = join(__current_dir, "./data/ceb_books_annot/x.dataset-query-sent-transformers.npz")
    dataset_st_embedding_response = join(__current_dir, "./data/ceb_books_annot/x.dataset-response-sent-transformers.txt")
    dataset_dialog_db_path = join(__current_dir, "./data/ceb_books_annot/dataset_dialog.sqlite")
    dataset_dialog_db_fold_path = join(__current_dir, "./data/ceb_books_annot/dataset_dialog_{fold_index}.sqlite")
    # spectrums-related data
    spectrum_per_user_count = 8
    spectrum_embedding_model_name = 'all-mpnet-base-v2'
    spectrum_features_norm = join(__current_dir, "./data/ceb_books_annot/x.spectrum-embeddings-norm.npz")
    spectrum_features_diff = join(__current_dir, "./data/ceb_books_annot/x.spectrum-embeddings-diff.npz")
    spectrum_speakers = join(__current_dir, "./data/ceb_books_annot/y.spectrum-speakers.npz")
    spectrum_preset = "prompt_top_k_{}_limited".format(str(spectrum_per_user_count))
    spectrum_st_embeddings = join(__current_dir, "./data/ceb_books_annot/x.spectrum-embeddings-sent-transformers-{preset}.npz")
    spectrum_prompts_filepath = join(__current_dir, "./data/ceb_books_annot/spectrum_speaker_prompts-{preset}.txt".format(preset=spectrum_preset))
    # This a models for the representation of the speakers.
    # ALOHA chatbot paper: https://arxiv.org/abs/1910.08293
    hla_training_config = MatrixTrainingConfig(top_n=100, regularization=100, iterations=500, factor=36,
                                               conf_scale=20, random_state=649128, safe_pass=0.2)
    hla_cluster_config = ClusterConfig(perc_cutoff=10, level2_limit=30, acceptable_overlap=10, weighted=False)
    hla_users_melted_filepath = join(books_storage, "features_melted.txt")
    hla_speaker_clusters_path = join(books_storage, "clusters.jsonl")
    hla_spectrums_limit = 40            # ALOHA parameter which is proposes to keep the most representative traits.
    hla_neg_set_speakers_limit = 10     # The overall process might take so much time is what becomes a reason of limit.
    hla_users_embedding_factor = join(__current_dir, "./data/ceb_books_annot/x.speakers-factor.npz")

    # ParlAI dataset creation related parameters.
    parlai_dataset_candidates_limit = 20
    parlai_dataset_persona_prefix = ""
    parlai_dataset_candidates_and_traits_shuffle_seed = 42
    parlai_dataset_filepath = join(__current_dir, "./data/ceb_books_annot/dataset_parlai_{}.zip")
    parlai_charmask_template = "_"      # We perform character masking for the ParlAI dataset of utterances.

    # separator in line between meta information and the actual content
    meta_sep = ": "
    dialogs_unknown_speaker = "UNKN-"

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

    @staticmethod
    def write_annotated_dialogs(iter_dialogs_and_speakers, filepath=None, print_sep=True):
        filepath = MyAPI.dialogs_filepath if filepath is None else filepath

        with open(filepath, "w") as file:
            it = tqdm(iter_dialogs_and_speakers, desc="writing dialogues")
            for dialog, recognized_speakers in it:
                assert(isinstance(dialog, OrderedDict))

                for speaker_id, segments in dialog.items():
                    assert(isinstance(segments, list))
                    assert(isinstance(recognized_speakers, dict))

                    sep = " " if print_sep is False else " {} ".format(BookDialogue.utterance_sep)
                    utterance = sep.join(segments)
                    speaker = recognized_speakers[speaker_id] \
                        if speaker_id in recognized_speakers else MyAPI.dialogs_unknown_speaker + str(speaker_id)
                    file.write("{speaker}: {utterance}\n".format(speaker=speaker, utterance=utterance))

                file.write('\n')

    @staticmethod
    def _read_annotated_dialogs(filepath=None):
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

    @staticmethod
    def write_speakers(speaker_names_list, filepath=None):
        assert(isinstance(speaker_names_list, list))

        filepath = MyAPI.filtered_speakers_filepath if filepath is None else filepath
        with open(filepath, "w") as f:
            for speaker_name in speaker_names_list:
                f.write("{}\n".format(speaker_name))

    @staticmethod
    def read_speakers(filepath=None):
        assert(isinstance(filepath, str) or filepath is None)

        filepath = MyAPI.filtered_speakers_filepath if filepath is None else filepath

        speakers = []
        with open(filepath, "r") as f:
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

    @staticmethod
    def iter_dialog_question_response_pairs(dialogs_filapath, dialogue_filter_func=None):
        """ dialogue_filter_func: func (speaker_name, dialogue)
                serves as a filtering function for a dialogue and a response speaker name.
        """

        qr_pair = []
        for line in MyAPI._read_annotated_dialogs(dialogs_filapath):

            if line is None:
                continue

            line = line.strip()
            qr_pair.append(line)

            # Keep the size of buffer equal 2.
            if len(qr_pair) > 2:
                qr_pair = qr_pair[1:]

            if len(qr_pair) != 2:
                continue

            r_speaker_name = MyAPI._get_meta(line)

            # We optionally filter buffers first.
            if dialogue_filter_func is not None:
                if not dialogue_filter_func(r_speaker_name, qr_pair):
                    continue

            yield r_speaker_name, qr_pair

    @staticmethod
    def write_dataset(dialog_qr_pairs_iter, filepath=None):
        # Read speakers to be considered first.
        speakers_set = set(MyAPI.read_speakers())

        filepath = MyAPI.dataset_filepath if filepath is None else filepath

        counter = Counter()
        with open(filepath, "w") as file:
            for speaker_name, qr_pair in dialog_qr_pairs_iter:
                assert(len(qr_pair) == 2)

                # We consider only such speakers that in predefined list.
                # We know we have a response to the known speaker.
                if MyAPI.dialogs_unknown_speaker not in speaker_name and speaker_name in speakers_set:
                    # We release content from the buffer.
                    MyAPI.write_dataset_buffer(file=file, buffer=qr_pair)
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
                    meta = MyAPI._get_meta(line)
                    text = line[len(meta) + len(MyAPI.meta_sep):]
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
    def calc_speakers_count(dataset_filepath, pbar=True):
        """ Folding with the even splits of the utterances.
        """
        partners_count = Counter()

        dialogs_it = MyAPI.iter_dataset_as_dialogs(
            MyAPI.read_dataset(keep_usep=False, split_meta=True,
                               dataset_filepath=dataset_filepath, pbar=pbar))

        for dialog in dialogs_it:
            partner_id = dialog[1][0]
            partners_count[partner_id] += 1

        return partners_count

    @staticmethod
    def save_speaker_spectrums(filepath, speaker_names, speaker_prompts):
        with open(filepath,  "w") as file:
            for i, p in enumerate(speaker_prompts):
                line = "".join([speaker_names[i], MyAPI.meta_sep, ",".join(p.split(' '))])
                file.write(line + "\n")

    @staticmethod
    def read_speaker_spectrums(filepath):
        with open(filepath, "r") as file:
            spectrums = {}
            for line in file.readlines():
                speaker_name, args = line.split(MyAPI.meta_sep)
                spectrums[speaker_name] = [a.strip() for a in args.split(',')]

        return spectrums
