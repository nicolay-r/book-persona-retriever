from api.gd import GuttenbergDialogApi
from api.ldc import LdcAPI
from core.dialogue.speaker_annotation import iter_speaker_annotated_dialogs


if __name__ == '__main__':

    ldc_api = LdcAPI()
    gd_api = GuttenbergDialogApi()

    it = iter_speaker_annotated_dialogs(
        dialog_segments_iter_func=gd_api.iter_dialog_segments(
            book_path_func=ldc_api.get_book_path,
            split_meta=True),
        prefix_lexicon=ldc_api.load_prefix_lexicon_en(),
        recognize_at_positions=ldc_api.dialogs_recognize_speaker_at_positions,
        total=ldc_api.get_total_books())

    ldc_api.write_annotated_dialogs(it)
