import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from core.speaker_annotation import iter_speaker_annotated_dialogs
from utils_my import MyAPI

my_api = MyAPI()

stat = my_api.calc_annotated_dialogs_stat(
    iter_dialogs_and_speakers=iter_speaker_annotated_dialogs(
        book_path_func=my_api.get_book_path,
        prefix_lexicon=my_api.load_prefix_lexicon_en())
)

print("recognized/utt: {}%".format(str(round(100.0 * stat["recognized"]/stat["utterances"], 2))))
print("recognized speakers per dialogs: {}".format(str(round(stat["recognized"]/stat["dialogs"], 2))))
# print("utterances per speaker: {}".format(str(round(stat["utterances_per_speaker"], 2))))
print("Total speakers: {}".format(len(stat["speakers_uc_stat"])))


df_dict = {
    "speaker": [],
    "utts": []
}

for k, v in stat["speakers_uc_stat"].items():
    df_dict["speaker"].append(k)
    df_dict["utts"].append(v)
speaker_utts_df = pd.DataFrame(df_dict)
g = sns.displot(speaker_utts_df, x="utts", kde=True)

#plt.ylim(0, 2500)
plt.xlim(0, 25)
plt.show()
