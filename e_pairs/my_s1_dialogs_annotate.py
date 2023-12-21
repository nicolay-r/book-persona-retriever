from core.dialogue.speaker_annotation import iter_speaker_annotated_dialogs
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


my_api = MyAPI()
gd_api = GuttenbergDialogApi()

it = iter_speaker_annotated_dialogs(
    dialog_segments_iter_func=gd_api.iter_dialog_segments(
        book_path_func=my_api.get_book_path,
        split_meta=True),
    prefix_lexicon=my_api.load_prefix_lexicon_en(),
    recognize_at_positions=my_api.dialogs_recognize_speaker_at_positions)

my_api.write_annotated_dialogs(it)
