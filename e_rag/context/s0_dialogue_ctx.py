import argparse
from os.path import join

from core.book.book_dialog import BookDialogue
from core.dialogue.speaker_annotation import parse_meta_speaker_id
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


def do_extract_speaker(utt):
    """ This is the main algorithm for speakers assignation.
        It is a rule-based approach that is related to key mentioned frames before the speaker names.
    """
    utterance_words = utt.split()
    for mention in args.key_mentions:

        # We consider the cases when we have a mentioned word.
        if mention not in utterance_words:
            continue

        # Check that the next word is speaker.
        frame_ind = utterance_words.index(mention)
        next_word = utterance_words[frame_ind + 1] if frame_ind + 1 < len(utterance_words) else None

        if next_word is None:
            continue

        return CEBApi.speaker_variant_to_speaker(next_word[1:], return_none=True)


def iter_content():

    gd_api = GuttenbergDialogApi()
    my_api = MyAPI()

    dialog_segments_iter = gd_api.iter_dialog_segments(book_path_func=my_api.get_book_path, split_meta=True)
    utterance_segments_iter = iter_by_utterances(dialogue_data=dialog_segments_iter)

    # We utilize the following keywords to match the exact speaker for the line.

    for book_id, data in utterance_segments_iter:

        main_context_speaker = None

        for utt_index, info in enumerate(data):
            meta, utt = info

            if not (meta[0] == BookDialogue.META_AUTHOR_COMMENT_LINE or
                    meta[0] == BookDialogue.META_END_OF_DIALOG_LINE):
                continue

            main_context_speaker = do_extract_speaker(utt)

            if main_context_speaker is not None:
                break

        # Skip the context for which we could not define the speaker.
        if main_context_speaker is None:
            continue

        buffer = []

        for utt_index, info in enumerate(data):
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
            is_last = utt_index == len(data)-1
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
            yield main_context_speaker, " ".join(buffer)


parser = argparse.ArgumentParser(
    description="Context Extraction from the dialogues of the literature novel books." +
                "We accomplish this via the rule-based approach of matching the key mentions.")

parser.add_argument('--max', dest='max_length', type=int, default=200)
parser.add_argument('--min', dest='min_length', type=int, default=100)
parser.add_argument('--segments', dest='segments_per_context', type=int, default=3)
parser.add_argument('--frames', dest='key_mentions', type=int, default=["said", "argreed", "asked"])

args = parser.parse_args()

CsvService.write(target=join(EMApi.output_dir, "utt_data.csv"), lines_it=iter_content())
