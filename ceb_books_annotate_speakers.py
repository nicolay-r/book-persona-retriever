from core.speaker_annotation import iter_speaker_annotated_dialogs
from utils_my import MyAPI


my_api = MyAPI()

my_api.write_annotated_dialogs(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        book_path_func=my_api.get_book_path,
        prefix_lexicon=my_api.load_prefix_lexicon_en())
)
