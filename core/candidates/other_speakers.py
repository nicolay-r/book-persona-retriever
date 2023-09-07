from core.candidates.base import CandidatesProvider


class OtherSpeakersProvider(CandidatesProvider):

    def __init__(self, speaker_ids, candidates_limit, get_trait_func):
        assert(callable(get_trait_func))
        self.__speaker_ids = speaker_ids
        self.__candidates_limit = candidates_limit
        self.__get_trait_func = get_trait_func

    def get_label(self, speaker_id):
        label = self.__get_trait_func(speaker_id)
        assert(isinstance(label, str))
        return label

    def provide_or_none(self, dialog_id, speaker_id, label, random):
        """Provide other speakers traits"""
        assert(label is None)

        # Select randomly the other candidates.
        speakers_to_select = random.sample(self.__speaker_ids, self.__candidates_limit + 1)
        candidates_to_select = [self.get_label(speaker_id) for speaker_id in speakers_to_select]

        # Remove the label if the related one is in the candidates_to_select.
        # NOTE: we use a bit different technique which is not required the presence of label.
        label_index = speakers_to_select.index(speaker_id) if speaker_id in speakers_to_select else None
        if label_index is not None:
            del candidates_to_select[label_index]

        return candidates_to_select[:self.__candidates_limit]
