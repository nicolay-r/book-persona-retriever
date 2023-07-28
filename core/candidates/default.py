from core.candidates.base import CandidatesProvider


class SameBookRandomCandidatesProvider(CandidatesProvider):
    """ Random candidates selection from the dataset.
        We consider the same "random" selection approach from the ALOHA paper:
            https://arxiv.org/pdf/1910.08293.pdf
    """

    def __init__(self, random_gen, iter_dialogs, candidates_limit, candidates_per_book):
        self.__random_gen = random_gen
        self.__candidates_limit = candidates_limit
        self.__candidates_per_book = self.__collect_candidates_responses_per_book(
            iter_dialogs=iter_dialogs, limit_per_book=candidates_per_book)

    @staticmethod
    def speaker_to_book_id(speaker_id):
        return int(speaker_id.split('_')[0])

    @staticmethod
    def __collect_candidates_responses_per_book(iter_dialogs, limit_per_book):
        assert (isinstance(limit_per_book, int) and limit_per_book > 0)

        candidates_per_book = {}
        for dialog in iter_dialogs:

            speaker_id, utterance = dialog[1]

            # Register book ID.
            book_id = SameBookRandomCandidatesProvider.speaker_to_book_id(speaker_id)
            if book_id not in candidates_per_book:
                candidates_per_book[book_id] = []

            target = candidates_per_book[book_id]

            if len(target) == limit_per_book:
                # Do not register the candidate.
                continue

            # Consider the potential candidate.
            target.append(utterance)

        return candidates_per_book

    def provide_or_none(self, dialog_id, speaker_id, label):
        # pick a copy of the candidates.
        book_id = SameBookRandomCandidatesProvider.speaker_to_book_id(speaker_id)
        related = list(iter(self.__candidates_per_book[book_id]))
        # remove already labeled candidate.
        if label in related:
            related.remove(label)
        # shuffle candidates.
        self.__random_gen.shuffle(related)
        # select the top of the shuffled.
        return related[:self.__candidates_limit]
