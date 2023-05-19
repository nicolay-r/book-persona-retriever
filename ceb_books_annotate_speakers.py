from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI

gd_api = GuttenbergDialogApi()
my_api = MyAPI()

found = 0
for b_id, dialog in gd_api.iter_dialog_segments(book_path_func=my_api.get_book_path):

    recognized = {}

    for i, segment in enumerate(dialog):

        # Considering only comments.
        if segment[0] not in ['#', '.']:
            continue

        # Taking meta information and text.
        terms = segment.split()
        meta = terms[0]
        text = terms[1:]

        speaker_id = int(meta[1:-1])

        # Do analysis.
        terms = gd_api.normalize_terms(text)

        ########################################################
        # Case 1.
        # For the case when first term is a mentioned character.
        ########################################################
        if len(terms) > 0 and gd_api.is_character(terms[0]):
            # Provide info.
            recognized[speaker_id] = terms[0]

        ########################################################
        # Case 2.
        # TODO.
        ########################################################

        ########################################################
        # Case 3.
        # TODO.
        ########################################################

    # print recognized.
    for segment in dialog:
        if segment[0] not in [">"]:
            continue

        # Taking meta information and text.
        terms = segment.split()
        meta = terms[0]
        text = terms[1:]

        speaker_id = int(meta[1:-1])

        u = "{{{}}}".format(recognized[speaker_id]) + segment \
            if speaker_id in recognized else segment

        print(u)

print(found)