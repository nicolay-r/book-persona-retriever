import numpy as np
import seaborn as sns
import pandas as pd
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


#######
# Data.
#######
X = np.array([[0, 0, 0],
              [0, 1, 1],
              [1, 0, 1],
              [1, 1, 1]])
##########
# Classes.
##########
y = [0, 1, 2, 3]

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