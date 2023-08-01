from collections import Counter
from core.speaker_annotation import iter_speaker_annotated_dialogs
from utils_my import MyAPI


def filter_speakers(ids_and_utterances_count_iter):
    """ Filtering algorithm of the speakers considered for the
        result dataset.
    """
    data = list(ids_and_utterances_count_iter)

    # Optional parameter. Keep the most frequent.
    if MyAPI.dataset_filter_speaker_total_speakers_count is not None:
        data = sorted(data, key=lambda item: item[1], reverse=True)
        data = data[:MyAPI.dataset_filter_speaker_total_speakers_count]

    for speaker_id, entries in data:

        # Optional check whether we meet the criteria of the min. amount of the utterances per speaker.
        if MyAPI.dataset_filter_speaker_min_utterances_per_char is not None:
            if entries < MyAPI.dataset_filter_speaker_min_utterances_per_char:
                continue

        yield speaker_id


local_counter = Counter()
def filter_dialog(speaker_id, dialogue):
    """ This function represents a dialog filtering procedure.
    """
    assert(isinstance(speaker_id, str))
    assert(isinstance(dialogue, list) and len(dialogue) == 2)

    # We limit by max amount of utterances per character.
    local_counter[speaker_id] += 1
    if local_counter[speaker_id] > MyAPI.dataset_filter_dialogue_max_utterances_per_char:
        return False

    # Limit by the minimum amount of words in the response.
    for utterance in dialogue:
        if len(utterance.split(' ')) < MyAPI.min_words_count_in_response:
            return False

    return True


my_api = MyAPI()
stat_origin = MyAPI.calc_annotated_dialogs_stat(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        book_path_func=my_api.get_book_path,
        prefix_lexicon=my_api.load_prefix_lexicon_en())
)

iter_speakers_stat = stat_origin["speakers_uc_stat"].items()
speaker_names_list = list(filter_speakers(iter_speakers_stat))

my_api.write_speakers(speaker_names_list)
my_api.write_dataset(dialogue_filter_func=filter_dialog)
