from core.dataset.filter_speakers import filter_response_speakers
from core.dataset.filter_qr_pairs import QRFilterFunctionObject
from utils_my import MyAPI


def get_dialog_qr_pairs_iter(desc):
    """ This method represents a main iterator of the qr-pairs data.
        with optionally provided filter of the dialogues.
    """
    return MyAPI.iter_dialog_question_response_pairs(
        dialogs_filapath=MyAPI.dialogs_filepath,
        dialogue_filter_func=QRFilterFunctionObject(),
        desc=desc)


MyAPI.write_speakers(list(filter_response_speakers(get_dialog_qr_pairs_iter(
    desc="Iter dialogues for composing speakers set"))))
MyAPI.write_dataset(dialog_qr_pairs_iter=get_dialog_qr_pairs_iter(
    "Iter dialogues for composing utterance dataset"))
