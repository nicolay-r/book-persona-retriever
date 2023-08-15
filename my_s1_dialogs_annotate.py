from core.dialogue.speaker_annotation import iter_speaker_annotated_dialogs
from test.ceb_books_utterance_speaker_analysis import gd_api
from utils_my import MyAPI


my_api = MyAPI()

my_api.write_annotated_dialogs(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        dialog_segments_iter_func=gd_api.iter_dialog_segments(my_api.get_book_path),
        prefix_lexicon=my_api.load_prefix_lexicon_en(),
        recognize_at_positions=my_api.dialogs_recognize_speaker_at_positions)
)
