from collections import Counter
from os.path import join

from core.plot import draw_hist_plot
from core.speaker_annotation import iter_speaker_annotated_dialogs
from utils_my import MyAPI

my_api = MyAPI()

stat_origin = MyAPI.calc_annotated_dialogs_stat(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        book_path_func=my_api.get_book_path,
        prefix_lexicon=my_api.load_prefix_lexicon_en())
)

########################################################
# Filtering speakers according to the particular amount.
########################################################
speaker_names_list = []
for speaker_name, entries in stat_origin["speakers_reply_stat"].items():
    if entries >= MyAPI.dataset_min_utterances_per_char:
        speaker_names_list.append(speaker_name)

print("Speakers origin: {}".format(len(stat_origin["speakers_uc_stat"])))
print("Speakers considered: {}".format(len(speaker_names_list)))

cc = Counter({k: c for k, c in stat_origin["speakers_reply_stat"].items()
              if c >= my_api.dataset_min_utterances_per_char})

draw_hist_plot(cc, n_bins=10,
               desc="Speakers reply stat origin",
               save_png_path=join(MyAPI.books_storage, "dataset_speakers_reply_origin.png"),
               show=False, asp_hor=12, asp_ver=2,
               min_val=0, max_val=len(cc))

##########################################################################
# Filter dialogs to the result dataset. Compose a Question->Response pair.
# Where response is always a known speaker, so whe know who we ask.
##########################################################################
c = Counter()


def __filter_buffer(speaker_id, buffer):
    assert(isinstance(speaker_id, str))
    assert(isinstance(buffer, list) and len(buffer) == 2)

    c[speaker_id] += 1
    if c[speaker_id] > MyAPI.dataset_max_utterances_per_char:
        return False

    for utterance in buffer:
        if len(utterance.split(' ')) < MyAPI.min_words_count_in_response:
            return False

    return True


my_api.write_speakers(speaker_names_list)
my_api.write_dataset(buffer_filter_func=__filter_buffer)
