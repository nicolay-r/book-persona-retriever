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
    if entries >= MyAPI.min_utterances_per_char:
        speaker_names_list.append(speaker_name)

print("Speakers origin: {}".format(len(stat_origin["speakers_uc_stat"])))
print("Speakers considered: {}".format(len(speaker_names_list)))

##########################################################################
# Filter dialogs to the result dataset. Compose a Question->Response pair.
# Where response is always a known speaker, so whe know who we ask.
##########################################################################
my_api.write_speakers(speaker_names_list)
my_api.write_dataset()
