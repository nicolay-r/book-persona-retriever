import numpy as np
from numpy import dot
from numpy.linalg import norm


def cosine_similarity(v1, v2):
    return dot(v1, v2) / (norm(v1) * norm(v2))


def normalize(v):
    return v / np.linalg.norm(v)


def random_choice_non_repetitive(v, p, size, to_list=False, take_less=False):
    assert(len(v) == len(p))
    p_norm = normalize(p)
    p_norm /= p_norm.sum()
    if take_less:
        size = min(size, len(v))
    choiced = np.random.choice(v, size=size, replace=False, p=p_norm)
    return choiced if to_list is False else list(choiced)
