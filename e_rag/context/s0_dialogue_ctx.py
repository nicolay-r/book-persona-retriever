from os.path import join

from core.book.book_dialog import BookDialogue
from utils_em import EMApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def iter_by_utterances(dialogue_data):

    for book_id, data in dialogue_data:

        buffer = []
        curr_speaker_id = None
        for info in data:

            meta, utt = info
            speaker_id = int(meta[1:-1])

            # Append the utterance into the buffer.
            if curr_speaker_id is None or (curr_speaker_id == speaker_id):
                curr_speaker_id = speaker_id
                buffer.append(info)
            elif len(buffer) > 0:
                # release the buffer.
                yield book_id, buffer
                buffer.clear()


gd_api = GuttenbergDialogApi()
my_api = MyAPI()

dialog_segments_iter = gd_api.iter_dialog_segments(
    book_path_func=my_api.get_book_path,
    split_meta=True)

utterance_segments_iter = iter_by_utterances(dialogue_data=dialog_segments_iter)


def filter_utterance_segments(buffer):

    # We are not interested in empty buffer.
    if len(buffer) == 0:
        return False

    # We consider long interaction.
    if len(buffer) < 3:
        return False

    # Write on met conditions.
    if not (300 > len(" ".join(buffer)) > 100):
        return False

    return True


with open(join(EMApi.output_dir, "utt_data.txt"), "w") as f:

    # We utilize the following keywords to match the exact speaker for the line.
    key_mentions = ["said", "argreed", "asked"]

    for book_id, data in utterance_segments_iter:

        pos = None
        for i, info in enumerate(data):
            meta, utt = info
            if meta[0] == BookDialogue.META_AUTHOR_COMMENT_LINE or meta[0] == BookDialogue.META_END_OF_DIALOG_LINE:
                for m in key_mentions:
                    if m + " {" in utt:
                        pos = i

        if pos is None:
            continue

        buffer = []
        c_ind = None
        for meta, utt in data[:pos+1]:

            ind = int(meta[1:-1])
            if ind != c_ind and c_ind is not None:
                if filter_utterance_segments(buffer):
                    f.write(" ".join(buffer) + "\n\n")
                    buffer.clear()

            c_ind = ind

            buffer.append(f"\"{utt}\"" if meta[0] == BookDialogue.META_DIALOGUE_LINE else utt)

        if filter_utterance_segments(buffer):
            f.write(" ".join(buffer) + "\n\n")
            buffer.clear()
