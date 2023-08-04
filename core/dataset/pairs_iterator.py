from core.dataset.filter_qr_pairs import QRFilterFunctionObject
from utils_my import MyAPI


def get_dialog_qr_pairs_iter(filepath, desc):
    """ This method represents a main iterator of the qr-pairs data.
        with optionally provided filter of the dialogues.
    """
    return MyAPI.iter_dialog_question_response_pairs(
        dialogs_filapath=filepath,
        dialogue_filter_func=QRFilterFunctionObject(),
        desc=desc)
