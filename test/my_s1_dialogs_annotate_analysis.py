from collections import Counter, OrderedDict

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

from core.dialogue.speaker_annotation import iter_speaker_annotated_dialogs
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def calc_annotated_dialogs_stat(iter_dialogs_and_speakers):
    """ iter_dialog_and_speakers: iter
            iter of data (dialog, recognized_speakers), where
                recognized_speakers (dict): {speaker_id: speaker}
                    speaker_id: BOOK_SPEAKER_VAR,
                    speaker: BOOK_SPEAKER.
    """
    counter = Counter()
    speaker_utts_stat = Counter()  # Per every utterance
    speaker_reply_stat = Counter()  # Per replies
    it = tqdm(iter_dialogs_and_speakers, desc="Calculating annotated dialogues stat")
    for dialog, recognized_speakers in it:
        assert (isinstance(dialog, OrderedDict))

        for utt_index, speaker_id in enumerate(dialog.keys()):
            assert (isinstance(recognized_speakers, dict))

            if speaker_id in recognized_speakers:
                counter["recognized"] += 1

                # register speaker
                speaker = recognized_speakers[speaker_id]
                speaker_utts_stat[speaker] += 1

                if utt_index > 0:
                    speaker_reply_stat[speaker] += 1

            counter["utterances"] += 1

        counter["dialogs"] += 1

    return {
        "recognized": counter["recognized"],
        "utterances": counter["utterances"],
        "dialogs": counter["dialogs"],
        "speakers_uc_stat": speaker_utts_stat,
        "speakers_reply_stat": speaker_reply_stat,
    }


my_api = MyAPI()
gd_api = GuttenbergDialogApi()

stat = calc_annotated_dialogs_stat(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        dialog_segments_iter_func=gd_api.iter_dialog_segments(
            book_path_func=my_api.get_book_path,
            split_meta=True),
        prefix_lexicon=my_api.load_prefix_lexicon_en(),
        recognize_at_positions=my_api.dialogs_recognize_speaker_at_positions)
)

print("original dialogs count: {}".format(stat["dialogs"]))
print("recognized per utterance: {}%".format(str(round(100.0 * stat["recognized"]/stat["utterances"], 2))))
print("recognized speakers per dialogs: {}".format(str(round(stat["recognized"]/stat["dialogs"], 2))))
print("utterances count: {}".format(str(stat["utterances"])))
print("utterances per dialog: {}".format(str(round(stat["utterances"]/stat["dialogs"], 2))))
print("Total speakers: {}".format(len(stat["speakers_uc_stat"])))


df_dict = {"utts": []}
for k, v in stat["speakers_uc_stat"].items():
    df_dict["utts"].append(v)
speaker_utts_df = pd.DataFrame(df_dict)

g = sns.displot(speaker_utts_df, x="utts", kde=True)

#plt.ylim(0, 2500)
plt.xlim(0, 25)
plt.show()
