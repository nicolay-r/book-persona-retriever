from os.path import basename

from core.dataset.filter_qr_pairs import QRFilterFunctionObject
from core.dialogue.utils import mask_text_entities
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def get_dialog_qr_pairs_iter(filepath, desc):
    """ This method represents a main iterator of the qr-pairs data.
        with optionally provided filter of the dialogues.
    """
    return MyAPI.iter_dialog_question_response_pairs(
        dialogs_filapath=filepath,
        dialogue_filter_func=QRFilterFunctionObject(),
        desc=desc)


def common_iter_dialogs(dialogs_dataset_filepath):
    """ We provide a common wrapping for reading because of the additional operations:
        the issue #18: https://github.com/nicolay-r/chatbot_experiments/issues/18
    """

    dialogs = MyAPI.iter_dataset_as_dialogs(
        MyAPI.read_dataset(
            keep_usep=False, split_meta=True,
            dataset_filepath=dialogs_dataset_filepath,
            desc="Iter dialogs: {}".format(basename(dialogs_dataset_filepath))))

    for dialog in dialogs:
        for d_ind in range(len(dialog)):
            meta, utterance = dialog[d_ind]

            # Mask text entities.
            utterance_masked = mask_text_entities(text=utterance,
                                                  is_term_has_char_func=GuttenbergDialogApi.has_character,
                                                  mask_template=MyAPI.parlai_charmask_template)

            dialog[d_ind] = (meta, utterance_masked)

        yield dialog
