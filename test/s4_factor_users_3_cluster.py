from os.path import join

import pandas as pd

from embeddings.aloha.cfg import ClusterConfig, MatrixTrainingConfig
from embeddings.aloha.cluster import CharCluster
from embeddings.aloha.matrix import MatrixWrapper
from utils_my import MyAPI


HLA_CLUSTER_CONFIG = ClusterConfig(perc_cutoff=10, level2_limit=30, acceptable_overlap=10, weighted=False)
HLA_TRAIN_CONFIG = MatrixTrainingConfig(top_n=100, regularization=100, iterations=200, factor=36,
                                        conf_scale=20, random_state=649128, safe_pass=0.2)

df = pd.read_csv(join(MyAPI.books_storage, "features_melted.txt"))
mw = MatrixWrapper(df, col1='user', col2='feature', col3="value")
mw.get_train(HLA_TRAIN_CONFIG, report_test=False)
cc = CharCluster(0, matrix_wrapper=mw)
pos, neg = cc.retrieve(config=HLA_CLUSTER_CONFIG)
print(pos)
print(neg)

