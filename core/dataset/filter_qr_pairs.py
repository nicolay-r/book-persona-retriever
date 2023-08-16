from collections import Counter

from core.dialogue.utils import iter_terms_with_speakers
from utils_ceb import CEBApi
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


class QRFilterFunctionObject(object):
    """ This is a main class that corresponds to filtering dialogs.
        We consider it as a class due to the additional parameters
        that find their application in the __call__ method
        (actual filtering)
    """

    def __init__(self):
        self.s_ctr = Counter()

    def __call__(self, *args, **kwargs):
        r_speaker_id, dialogue = args

        assert(isinstance(r_speaker_id, str) or r_speaker_id is None)
        assert(isinstance(dialogue, list) and len(dialogue) == 2)

        # We do not consider dialogue with the unknown output speaker name.
        if r_speaker_id is None:
            return False

        # We additionally check the correctness of the composed ID.
        # In some cases we may end up with such entries as "_You" or "_I"
        if not CEBApi.is_speaker_id(r_speaker_id):
            return False

        if self.s_ctr[r_speaker_id] >= MyAPI.dataset_filter_dialogue_max_utterances_per_speaker:
            return False

        # We consider only those utterances that is not contain information
        # or refer to other speakers.
        r_speakers = []
        iter_terms_with_speakers(terms=dialogue[1].split(' '),
                                 is_term_has_char_func=GuttenbergDialogApi.has_character,
                                 map_func=lambda x: r_speakers.append(x))
        if len(r_speakers) > MyAPI.dataset_filter_other_speakers_in_response:
            return False

        # Limit by the minimum amount of words in the response.
        for utterance in dialogue:
            if len(utterance.split(' ')) < MyAPI.dataset_min_words_count_in_response:
                return False

        self.s_ctr[r_speaker_id] += 1

        return True
