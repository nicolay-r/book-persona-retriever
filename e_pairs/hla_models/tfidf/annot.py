from api.ceb import CEBApi
from api.gd import GuttenbergDialogApi


def annot_in_text(texts_and_speakervars_iter):

    gd_api = GuttenbergDialogApi()

    d = {}
    for text, speakers in texts_and_speakervars_iter:
        assert (isinstance(text, str))
        assert (isinstance(speakers, list))

        norm_terms = gd_api.normalize_terms(text.split())
        speaker = CEBApi.speaker_variant_to_speaker(speakers[0])

        # TODO. Provide another model there based on tf-idf.

    return d
