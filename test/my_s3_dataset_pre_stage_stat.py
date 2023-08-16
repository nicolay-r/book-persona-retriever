from collections import Counter

from utils_my import MyAPI

fold_index = None
filepath = MyAPI.dataset_fold_filepath.format(fold_index=fold_index) \
    if fold_index is not None else MyAPI.dataset_filepath

it = MyAPI.iter_dialog_question_response_pairs(dialogs_filapath=filepath, dialogue_filter_func=None)

c = Counter()
for _, dialog in it:
    c["dialog"] += 1

print("Query-Response pairs count (original, non-filtered):", c["dialog"])

