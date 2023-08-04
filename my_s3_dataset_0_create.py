from core.dataset.filter_speakers import filter_response_speakers
from core.dataset.pairs_iterator import get_dialog_qr_pairs_iter
from utils_my import MyAPI

filepath = MyAPI.dialogs_filepath

MyAPI.write_speakers(list(filter_response_speakers(get_dialog_qr_pairs_iter(
    filepath=filepath, desc="Iter dialogues for composing speakers set"))))
MyAPI.write_dataset(dialog_qr_pairs_iter=get_dialog_qr_pairs_iter(
    filepath=filepath, desc="Iter dialogues for composing utterance dataset"))
