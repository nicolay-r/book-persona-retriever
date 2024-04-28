from core.dataset.filter_speakers import filter_response_speakers
from core.dataset.pairs_iterator import get_dialog_qr_pairs_iter
from utils_my import MyAPI


if __name__ == '__main__':

    src_filepath = MyAPI.dialogs_filepath
    MyAPI.write_speakers(list(filter_response_speakers(get_dialog_qr_pairs_iter(
        filepath=src_filepath, desc="Iter dialogues for composing speakers set"))))
    MyAPI.write_dataset(speakers_set=set(MyAPI.read_speakers()),
                        dialog_qr_pairs_iter=get_dialog_qr_pairs_iter(
                            filepath=src_filepath, desc="Iter dialogues for composing utterance dataset"))
