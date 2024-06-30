from api.ldc import LdcAPI
from core.dataset.filter_speakers import filter_response_speakers
from core.dataset.pairs_iterator import get_dialog_qr_pairs_iter


if __name__ == '__main__':

    src_filepath = LdcAPI.dialogs_filepath
    LdcAPI.write_speakers(list(filter_response_speakers(get_dialog_qr_pairs_iter(
        filepath=src_filepath, desc="Iter dialogues for composing speakers set"))))
    LdcAPI.write_dataset(speakers_set=set(LdcAPI.read_speakers()),
                         dialog_qr_pairs_iter=get_dialog_qr_pairs_iter(
                            filepath=src_filepath, desc="Iter dialogues for composing utterance dataset"))
