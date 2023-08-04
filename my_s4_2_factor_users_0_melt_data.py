from tqdm import tqdm

from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.spectrum_features_norm))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

filter_func = lambda val: val > 0.3 or val < -0.3
with open(MyAPI.hla_melted_data_filepath, "w") as out:
    out.write("user,feature,value\n")
    for u_ind, name in tqdm(enumerate(y)):
        for item_ind, x in enumerate(X[u_ind]):
            # We use this limitation to guarantee that there is a one criteria for every speaker,
            # and hence the result amount of speakers will remain the same.
            if item_ind > 0:
                if not filter_func(x):
                    continue
            out.write("{},{},{}\n".format(u_ind, item_ind, round(x, 2)))
