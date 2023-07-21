import math
from collections import Counter
import logging
from embeddings.aloha.cfg import ClusterConfig
logger = logging.getLogger('example_logger')


class CharCluster:
    """Target character cluster manager.

    The manager build character cluster based on one cluster provided.
    """
    def __init__(self, target, matrix_wrapper):
        self.target = target
        self.mw = matrix_wrapper

    def _expand(self, l1, l2, aco, weighted, log_scale, limits):
        """Communities expand from target as center by two levels. For details, refer to paper and docs.

        Returns:
            positive characters: list of character id for positives, format: (character id, freq, score).
            negative characters: set of character id for negatives.
        """
        # level 2 holder. Key: candidate category id; value: (freq, score)
        level1 = self.mw.get_similar_user(self.target, top_n=l1)

        # expand level 1 and further level 2
        counter = Counter()
        logger.info('Level 1 total {}'.format(len(level1)))
        for char1, _ in level1:
            for char2, _ in self.mw.get_similar_user(char1, top_n=l2):
                if limits and (char2 not in limits):
                    continue
                counter[char2] += 1

        # build positive / negative character set
        _pos, _neg = [], set()
        logger.info('Level 2 total {}'.format(len(counter)))
        for char_id, freq in counter.most_common():
            score = 1
            if weighted:
                if log_scale:
                    score = math.log(freq)
                else:
                    score = freq
            if freq >= aco:
                _pos.append((char_id, freq, score,))
            else:
                _neg.add(char_id)
        return _pos, _neg

    def retrieve(self, config: ClusterConfig, limits=None):
        """Retrieve positive and negative characters to target.
        Returns:
            positive characters: list of character id for positives, format: (character id, freq, score).
            negative characters: set of character id for negatives.
        """
        l1 = config.l1 if config.l1 is not None else self.mw.m1_count
        l1 = min(int(float(self.mw.m1_count) * config.perc_cutoff / 100), l1)
        l2 = config.l2 if config.l2 is not None else self.mw.m1_count
        logger.info('Considering {} out of L1: {}, L2 {} top ranked characters.'.format(l1, l2, self.mw.m1_count))

        positives, negatives = self._expand(l1, l2, config.aco, config.weighted, config.log_scale, limits=limits)
        return positives, negatives
