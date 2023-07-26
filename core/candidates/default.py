import random
from core.candidates.base import CandidatesProvider
from utils_my import MyAPI


class SameBookRandomCandidatesProvider(CandidatesProvider):
    """ Random candidates selection from the dataset.
        We consider the same "random" selection approach from the ALOHA paper:
            https://arxiv.org/pdf/1910.08293.pdf
    """

    def __init__(self, dataset_filepath, candidates_limit, candidates_per_book):
        self.__candidates_limit = candidates_limit
        self.__candidates_per_book = self.__create_dict(dataset_filepath=dataset_filepath,
                                                        limit_per_book=candidates_per_book)

    @staticmethod
    def speaker_to_book_id(speaker_id):
        return int(speaker_id.split('_')[0])

    @staticmethod
    def __create_dict(dataset_filepath, limit_per_book):
        assert (isinstance(limit_per_book, int) and limit_per_book > 0)

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
            speaker_id = args[0]
            book_id = SameBookRandomCandidatesProvider.speaker_to_book_id(speaker_id)
            if book_id not in candidates:
                candidates[book_id] = []

            target = candidates[book_id]

            if len(target) == limit_per_book:
                # Do not register the candidate.
                continue

            # Consider the potential candidate.
            target.append(args[1])

        return candidates

    def provide_or_none(self, speaker_id, label):
        # pick a copy of the candidates.
        book_id = SameBookRandomCandidatesProvider.speaker_to_book_id(speaker_id)
        related = list(iter(self.__candidates_per_book[book_id]))
        # remove already labeled candidate.
        if label in related:
            related.remove(label)
        # shuffle candidates.
        random.shuffle(related)
        # select the top of the shuffled.
        return related[:self.__candidates_limit]


