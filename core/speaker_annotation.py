from collections import OrderedDict

from utils_gd import GuttenbergDialogApi


def iter_speaker_annotated_dialogs(book_path_func, prefix_lexicon=None):
    """ This is a speaker annotation algorithm based on guttenberg-dialog
        project with additional annotation from my side (Rusnachenko Nicolay),
        that provides segmenting and author text part (comments) in between
        the segments.
    """
    assert(isinstance(prefix_lexicon, set) or prefix_lexicon is None)

    gd_api = GuttenbergDialogApi()

    for b_id, dialog_segments in gd_api.iter_dialog_segments(book_path_func):

        speakers = set()
        recognized_speakers = {}

        for i, segment in enumerate(dialog_segments):

            # Considering only comments.
            if segment[0] not in ['#', '.']:
                continue

            # Taking meta information and text.
            terms = segment.split()
            meta = terms[0]
            text = terms[1:]

            speaker_id = int(meta[1:-1])
            speakers.add(speaker_id)

            # Do analysis.
            terms = gd_api.normalize_terms(text)

            ########################################################
            # Annotation algorithm.
            ########################################################
            recognized = False
            if len(terms) > 0 and gd_api.is_character(terms[0]):
                # Provide info.
                recognized_speakers[speaker_id] = terms[0]
                recognized = True

            # Annotation based on lexicon and prefix.
            for k in [1, 2, 3]:
                if prefix_lexicon is not None:
                    if len(terms) > k and gd_api.is_character(terms[k]):
                        if ' '.join(terms[:k]) in prefix_lexicon:
                            # Provide info.
                            recognized_speakers[speaker_id] = terms[k]
                            recognized = True
                            break

            #if not recognized:
            #    print(terms)

        # Compose to format of actual dialog between speakers
        dialog = OrderedDict()
        for segment in dialog_segments:

            if segment[0] not in [">"]:
                continue

            # Taking meta information and text.
            terms = segment.split()
            meta = terms[0]
            text = ' '.join(terms[1:])

            # Initialize the list for the particular speaker.
            speaker_id = int(meta[1:-1])
            if speaker_id not in dialog:
                dialog[speaker_id] = []

            dialog[speaker_id].append(text)

        yield dialog, recognized_speakers
