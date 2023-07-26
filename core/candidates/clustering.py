import json
import math

from tqdm import tqdm

from utils_my import MyAPI
from utils import CACHE_DIR

from sentence_transformers import SentenceTransformer
from core.candidates.base import CandidatesProvider


class ALOHANegBasedClusteringProvider(CandidatesProvider):
    """ Cluster based approach.
        Every cluster provides list of positive and negative characters.
        For candidates we consider utterances from "Negative" characters.
        We also select the most relevant, which makes our interest in embedded vectors for the related utterances.
        We consider the same "random" selection approach from the ALOHA paper:
            https://arxiv.org/pdf/1910.08293.pdf
    """

    def __init__(self, dataset_filepath, cluster_filepath, limit_per_char,
                 utterances_filepath, vectors_filepath, candidates_limit,
                 closest_candidates_limit=100):
        assert(isinstance(dataset_filepath, str))
        assert(isinstance(cluster_filepath, str))
        assert(isinstance(utterances_filepath, str))
        assert(isinstance(vectors_filepath, str))
        self.__candidates_limit = candidates_limit
        self.__closest_candidates_limit = closest_candidates_limit
        self.__neg_clusters_per_speaker = self.__read_cluster(cluster_filepath)
        self.__candidates_per_speaker = self.__create_dict(
            dataset_filepath=dataset_filepath, limit_per_char=limit_per_char)

        self.__model = SentenceTransformer('all-mpnet-base-v2', cache_folder=CACHE_DIR)

    @staticmethod
    def __read_cluster(cluster_filepath):
        neg_speakers = {}
        with open(cluster_filepath, "r") as f:
            for line in f.readlines():
                data = json.loads(line)
                speaker_id = data["speaker_id"]
                ids = data["neg"]
                neg_speakers[speaker_id] = ids
        return neg_speakers

    @staticmethod
    def __create_dict(dataset_filepath=None, limit_per_char=100):
        assert (isinstance(limit_per_char, int) and limit_per_char > 0)

        lines = []

        candidates = {}
        for args in MyAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=dataset_filepath):
            if args is None:
                lines.clear()
                continue

            lines.append(args)

            if len(lines) < 2:
                continue

            # Here is type of data we interested in.
            speaker = args[0]

            if speaker not in candidates:
                candidates[speaker] = []
            target = candidates[speaker]

            if len(target) == limit_per_char:
                # Do not register the candidate.
                continue

            # Consider the potential candidate.
            target.append(args[1])

        return candidates

    @staticmethod
    def cosine_similarity(v1, v2):
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i];
            y = v2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy / math.sqrt(sumxx * sumyy)

    def provide(self, speaker_id, label):

        # Compose list of the NON-relevant candidates.
        neg_candidates = []
        for s_id in self.__neg_clusters_per_speaker[speaker_id]:
            neg_candidates.extend(self.__candidates_per_speaker[s_id])

        # Calculate embedding vectors.
        vectors = []
        for c in neg_candidates:
            vectors.append(self.__model.encode(c))

        label_vector = self.__model.encode(label)
        vvv = [(i, self.cosine_similarity(label_vector, v)) for i, v in enumerate(vectors)]
        most_similar_first = sorted(vvv, key=lambda item: item[1], reverse=True)

        ordered_neg_candidates = [neg_candidates[i] for i, _ in most_similar_first]
        selected = ordered_neg_candidates[:self.__closest_candidates_limit]

        if label in selected:
            selected.remove(label)

        return selected[:self.__candidates_limit]
