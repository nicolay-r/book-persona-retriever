from collections import Counter

from tqdm import tqdm

from api.gd import GuttenbergDialogApi
from api.ldc import LdcAPI
from core.book.book_dialog import BookDialogue


fold_index = None
filepath = LdcAPI.dialogs_filepath
gd_api = GuttenbergDialogApi()
ldc_api = LdcAPI()

it_segments = gd_api.iter_dialog_segments(book_path_func=ldc_api.get_book_path, split_meta=True)
it_dialogs = LdcAPI._read_annotated_dialogs(filepath=filepath)
it_qr_pairs = LdcAPI.iter_dialog_question_response_pairs(dialogs_filepath=filepath, dialogue_filter_func=None)

c = Counter()
for book_id, data in tqdm(it_segments):
    for meta, _ in data:
        c["segments"] += 1
        c[f"segments-{meta[0]}"] += 1
for line in it_dialogs:
    if line is None:
        c["dialogs"] += 1
for _ in it_qr_pairs:
    c["qr_pairs"] += 1

comments = c[f"segments-{BookDialogue.META_AUTHOR_COMMENT_LINE}"] +\
           c[f"segments-{BookDialogue.META_END_OF_DIALOG_LINE}"]

utterances = c[f"segments-{BookDialogue.META_DIALOGUE_LINE}"] +\
             c[f"segments-{BookDialogue.META_BEGIN_OF_DIALOG_LINE}"]

print("----")
print("Segments (original):", c["segments"])
print("Segments Utterances (original):", utterances)
print("Segments Utterances (original, %):", round(100 * utterances / c["segments"], 2))
print("Segments Comments (original):", comments)
print("Segments Comments (original, %):", round(100 * comments / c["segments"], 2))
print("----")
print("Dialogues (original, non-filtered):", c["dialogs"])
print("----")
print("Query-Response pairs count (original, non-filtered):", c["qr_pairs"])
