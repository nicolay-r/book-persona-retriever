from core.candidates.base import CandidatesProvider


class UniformCandidatesProvider(CandidatesProvider):
    """ Random candidates selection from the dataset.
        We consider the same "random" selection approach from the ALOHA paper:
            https://arxiv.org/pdf/1910.08293.pdf
    """

    def __init__(self, random_gen, iter_dialogs, candidates_limit):
        self.__random_gen = random_gen
        self.__candidates_limit = candidates_limit
        self.__candidates = self.__collect_candidates(iter_dialogs=iter_dialogs)
        self.__candidate_indices = list(range(len(self.__candidates)))

    @staticmethod
    def __collect_candidates(iter_dialogs):
        candidates = set()
        for dialog in iter_dialogs:
            _, utterance = dialog[1]
            candidates.add(utterance)
        return [c for c in candidates]

    def provide_or_none(self, dialog_id, speaker_id, label):
        """ NOTE: we consider canidates+1 to cover case of the
            potential presence of `label` in the extracted list.
        """
        indices_to_select = self.__random_gen.sample(self.__candidate_indices, self.__candidates_limit+1)
        candidates_to_select = [self.__candidates[ind] for ind in indices_to_select]
        label_index = candidates_to_select.index(label) if label in candidates_to_select else None
        if label_index is not None:
            del candidates_to_select[label_index]
        return candidates_to_select[:self.__candidates_limit]
