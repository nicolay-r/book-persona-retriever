import json
import math

from tqdm import tqdm

from core.database.sqlite3_api import NpArraySupportDatabaseTable
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

    def __init__(self, dataset_filepath, cluster_filepath, vectorized_utterances_filepath,
                 embedding_model_name, neg_speakers_limit=20, candidates_limit=20,
                 cache_embeddings_in_memory=False):
        assert(isinstance(dataset_filepath, str))
        assert(isinstance(cluster_filepath, str))
        assert(isinstance(vectorized_utterances_filepath, str))

        self.__candidates_limit = candidates_limit
        self.__neg_speakers_limit = neg_speakers_limit

        self.__neg_clusters_per_speaker = self.__read_cluster(cluster_filepath)
        self.__model = SentenceTransformer(embedding_model_name, cache_folder=CACHE_DIR)

        self.__vp = NpArraySupportDatabaseTable()
        self.__vp.connect(vectorized_utterances_filepath)
        self.__vp_cache = None

        # Caching in memory.
        if cache_embeddings_in_memory:
            self.__vp_cache = {}
            for speaker_id, utterance, vector in tqdm(self.__vp.select_from_table(), desc="caching"):
                if speaker_id not in self.__vp_cache:
                    self.__vp_cache[speaker_id] = []
                self.__vp_cache[speaker_id].append((utterance, vector))

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
    def cosine_similarity(v1, v2):
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i];
            y = v2[i]
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy / math.sqrt(sumxx * sumyy)

    def __iter_from_database(self, neg_speakers):
        where_clause = 'speakerid in ({})'.format(",".join(['"{}"'.format(s) for s in neg_speakers]))
        return self.__vp.select_from_table(where=where_clause)

    def __iter_from_cache(self, neg_speakers):
        assert(isinstance(neg_speakers, list))
        print(neg_speakers)
        for speaker_id in neg_speakers:
            if speaker_id in self.__vp_cache:
                for info in self.__vp_cache[speaker_id]:
                    utterance, vector = info
                    yield (speaker_id, utterance, vector)

    def provide_or_none(self, speaker_id, label):

        # In some cases we may end up with the missed speaker.
        if speaker_id not in self.__neg_clusters_per_speaker:
            return None

        # Compose a SQL-request to obtain vectors and utterances.
        neg_speakers = self.__neg_clusters_per_speaker[speaker_id][:self.__neg_speakers_limit]

        # Compose WHERE clause that filters the relevant speakers.
        data_it = self.__iter_from_database(neg_speakers) \
            if self.__vp_cache is None else self.__iter_from_cache(neg_speakers)

        vectors = []
        neg_candidates = []
        for speaker_id, utterance, vector in data_it:
            vectors.append(vector)
            neg_candidates.append(utterance)

        label_vector = self.__model.encode(label)
        vvv = [(i, self.cosine_similarity(label_vector, v)) for i, v in enumerate(vectors)]
        most_similar_first = sorted(vvv, key=lambda item: item[1], reverse=True)

        selected = [neg_candidates[i] for i, _ in most_similar_first]

        if label in selected:
            selected.remove(label)

        return selected[:self.__candidates_limit]
