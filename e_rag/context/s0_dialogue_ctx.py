import argparse
from os.path import join

from tqdm import tqdm

import utils
from core.book.book_dialog import BookDialogue
from core.dialogue.speaker_annotation import parse_meta_speaker_id, try_recognize
from utils import CsvService
from utils_ceb import CEBApi
from utils_em import EMApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_by_utterances(dialogue_data):

    for book_id, data in dialogue_data:

        buffer = []
        curr_speaker_id = None
        for info in data:

            meta, utt = info
            speaker_id = parse_meta_speaker_id(meta)

            # Append the utterance into the buffer.
            if curr_speaker_id is None or (curr_speaker_id == speaker_id):
                curr_speaker_id = speaker_id
                buffer.append(info)
            elif len(buffer) > 0:
                # release the buffer.
                yield book_id, buffer
                buffer.clear()


def filter_utterance_segments(buffer):

    # We are not interested in empty buffer.
    if len(buffer) == 0:
        return False

    # We consider long interaction.
    if len(buffer) < args.segments_per_context:
        return False

    # Write on met conditions.
    if not (args.max_length > len(" ".join(buffer)) > args.min_length):
        return False

    return True


def do_pattern_mathing_extract(utterance_words, patterns):
    """ This is the main algorithm for speakers assignation.
        It is a rule-based approach that is related to key mentioned frames before the speaker names.
    """
    for mention in patterns:

        # We consider the cases when we have a mentioned word.
        if mention not in utterance_words:
            continue

        # Check that the next word is speaker.
        frame_ind = utterance_words.index(mention)

        # We consider that it is the first word.
        if frame_ind != 0:
            continue

        next_word = utterance_words[frame_ind + 1] if frame_ind + 1 < len(utterance_words) else None

        if next_word is None:
            continue

        return CEBApi.speaker_variant_to_speaker(next_word[1:], return_none=True)


def iter_content(utterance_segments_iter, se_algo=None):
    assert(callable(se_algo) or se_algo is None)

    # We utilize the following keywords to match the exact speaker for the line.

    for book_id, utt_data in tqdm(utterance_segments_iter, "Iter dialogue utterances"):

        main_context_speaker = None

        for meta, segment in utt_data:

            if not (meta[0] == BookDialogue.META_AUTHOR_COMMENT_LINE or
                    meta[0] == BookDialogue.META_END_OF_DIALOG_LINE):
                continue

            main_context_speaker = se_algo(segment.split())

            if main_context_speaker is not None:
                break

        # Skip the context for which we could not define the speaker.
        if main_context_speaker is None:
            continue

        buffer = []

        for utt_index, info in enumerate(utt_data):
            meta, utt = info

            # Masking character names.
            utterance_words = utt.split()
            for w_ind, w in enumerate(utterance_words):
                s_id = CEBApi.speaker_variant_to_speaker(w[1:], return_none=True)
                if s_id is None:
                    continue
                assert("_" in main_context_speaker)
                utterance_words[w_ind] = "X" if s_id == main_context_speaker else "Y"

            utt = " ".join(utterance_words)

            # Formatting.
            fmt_s = utt
            is_last = utt_index == len(utt_data) - 1
            if meta[0] == BookDialogue.META_DIALOGUE_LINE and not is_last:
                fmt_s = f"\"{utt}\","
            elif meta[0] == BookDialogue.META_DIALOGUE_LINE and is_last:
                fmt_s = f"\"{utt}\"."
            elif meta[0] == BookDialogue.META_AUTHOR_COMMENT_LINE and not is_last:
                fmt_s = f"- {utt} -"
            elif meta[0] == BookDialogue.META_AUTHOR_COMMENT_LINE and is_last:
                fmt_s = f"- {utt}" + ("." if utt[-1] != '.' else "")

            buffer.append(fmt_s)

        if filter_utterance_segments(buffer):
            yield main_context_speaker, \
                  ceb_api.get_char_name(main_context_speaker), \
                  " ".join(buffer)


parser = argparse.ArgumentParser(
    description="Context Extraction from the dialogues of the literature novel books.")

se_algorithms = {
    "default": lambda terms: CEBApi.speaker_variant_to_speaker(
        speaker_variant=str(
            try_recognize(gd_api.normalize_terms(terms),
                          prefix_lexicon=my_api.load_prefix_lexicon_en(),
                          k_list=my_api.dialogs_recognize_speaker_at_positions,
                          is_character_func=GuttenbergDialogApi.is_character)[1]
        ),
        return_none=True),
    "strict": lambda terms: do_pattern_mathing_extract(terms, patterns=args.key_mentions),
}


parser.add_argument('--max', dest='max_length', type=int, default=300)
parser.add_argument('--min', dest='min_length', type=int, default=100)
parser.add_argument('--books', dest='books_dir', type=str, default=join(EMApi.output_dir, "books"))
parser.add_argument('--segments', dest='segments_per_context', type=int, default=2)
parser.add_argument('--se-mode', dest='se_mode', type=str, default="default", choices=list(se_algorithms.keys()))
parser.add_argument('--frames', dest='key_mentions', type=str, default=["said", "argreed", "asked", "replied", "cried"])
parser.add_argument('--output', dest="output", type=str, default=None)


args = parser.parse_args()


gd_api = GuttenbergDialogApi(dialogues_source=join(utils.PROJECT_DIR, "./data/filtered/en/dialogs_clean.txt"))
my_api = MyAPI(books_root=args.books_dir)

ceb_api = CEBApi()
ceb_api.read_char_map()

utterance_segments_iter = iter_by_utterances(
    dialogue_data=gd_api.iter_dialog_segments(
        book_path_func=my_api.get_book_path, split_meta=True, skip_missed_books=True))

CsvService.write(target=join(EMApi.output_dir, f"dialogue-ctx-{args.se_mode}.csv") if args.output is None else args.output,
                 lines_it=iter_content(utterance_segments_iter, se_algo=se_algorithms[args.se_mode]),
                 header=["speaker_id", "speaker_name", "text"])
