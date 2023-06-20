import seaborn as sns
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from core.utils_npz import NpzUtils
from utils_my import MyAPI

X = NpzUtils.load(MyAPI.spectrum_embeddings)
y = NpzUtils.load(MyAPI.spectrum_speakers)

tsne = TSNE(n_components=2, learning_rate='auto', init='random', perplexity=3)
emb_X = tsne.fit_transform(X)
tsne_data = pd.DataFrame()
tsne_data["y"] = y
print(emb_X)
tsne_data["comp-1"] = emb_X[:, 0]
tsne_data["comp-2"] = emb_X[:, 1]
print(tsne_data["comp-1"])
print(tsne_data["comp-2"])
sns.scatterplot(x="comp-1", y="comp-2", hue=tsne_data.y.tolist(),
                data=tsne_data).set(title="Scikit learn TSNE")

plt.show()