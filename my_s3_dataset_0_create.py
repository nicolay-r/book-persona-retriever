from collections import Counter
from utils_my import MyAPI


def filter_response_speakers(dialogue_qr_pairs_it):
    """ Filtering algorithm of the speakers considered for the result dataset.
    """

    speaker_ids = []
    speaker_entries = Counter()
    for r_speaker_id, _ in dialogue_qr_pairs_it:
        speaker_entries[r_speaker_id] += 1
        speaker_ids.append(r_speaker_id)

    # Optional parameter. Keep the most frequent.
    if MyAPI.dataset_filter_speaker_total_speakers_count is not None:
        ordered_speaker_ids = sorted(speaker_ids, key=lambda speaker_id: speaker_entries[speaker_id], reverse=True)
        speaker_ids = ordered_speaker_ids[:MyAPI.dataset_filter_speaker_total_speakers_count]

    for speaker_id in speaker_ids:

        entries = speaker_entries[speaker_id]

        # Optional check whether we meet the criteria of the min. amount of the utterances per speaker.
        if MyAPI.dataset_filter_speaker_min_utterances_per_char is not None:
            if entries < MyAPI.dataset_filter_speaker_min_utterances_per_char:
                continue

        yield speaker_id


class DialogFilterFunctionObject(object):
    """ This is a main class that corresponds to filtering dialogs.
        We consider it as a class due to the additional parameters
        that find their application in the __call__ method
        (actual filtering)
    """

    def __init__(self):
        self.local_counter = Counter()

    def __call__(self, *args, **kwargs):
        speaker_id, dialogue = args
        assert(isinstance(speaker_id, str))
        assert(isinstance(dialogue, list) and len(dialogue) == 2)

        # We limit by max amount of utterances per character.
        self.local_counter[speaker_id] += 1
        if self.local_counter[speaker_id] > MyAPI.dataset_filter_dialogue_max_utterances_per_char:
            return False

        # Limit by the minimum amount of words in the response.
        for utterance in dialogue:
            if len(utterance.split(' ')) < MyAPI.dataset_min_words_count_in_response:
                return False

        return True


def get_dialog_qr_pairs_iter(desc):
    """ This method represents a main iterator of the qr-pairs data.
        with optionally provided filter of the dialogues.
    """
    return MyAPI.iter_dialog_question_response_pairs(
        dialogs_filapath=MyAPI.dialogs_filepath,
        dialogue_filter_func=DialogFilterFunctionObject(),
        desc=desc)


MyAPI.write_speakers(list(filter_response_speakers(get_dialog_qr_pairs_iter(
    desc="Iter dialogues for composing speakers set"))))
MyAPI.write_dataset(dialog_qr_pairs_iter=get_dialog_qr_pairs_iter(
    "Iter dialogues for composing utterance dataset"))
