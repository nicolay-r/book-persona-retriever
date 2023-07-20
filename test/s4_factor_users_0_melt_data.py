from os.path import join

from tqdm import tqdm

from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = list(NpzUtils.load(MyAPI.spectrum_features_norm))
y = list(NpzUtils.load(MyAPI.spectrum_speakers))

ffunc = lambda val: val > 0.3 or val < -0.3
with open(join(MyAPI.books_storage, "features_melted.txt"), "w") as out:
    out.write("user,feature,value\n")
    for u_ind, name in tqdm(enumerate(y)):
        for item_ind, x in enumerate(X[u_ind]):
            if not ffunc(x):
                continue
            out.write("{},{},{}\n".format(u_ind, item_ind, round(x, 2)))