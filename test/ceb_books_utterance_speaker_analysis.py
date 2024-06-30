
# Setup API.
from api.gd import GuttenbergDialogApi
from api.ldc import LdcAPI

ldc_api = LdcAPI()
gd_api = GuttenbergDialogApi()


def calc_comments_count(c):
    count = 0
    for v in c.values():
        count += sum([len(a) for a in v if isinstance(a, list)])
    return count


def total_dialogs_count(c):
    return sum([len(v) for v in c.values()])


# Assess total amount of extracted comments.
all_dialogs = {}
for book_id, lines in gd_api.filter_comment_with_speaker_at_k(book_path_func=ldc_api.get_book_path, k=None):
    if book_id not in all_dialogs:
        all_dialogs[book_id] = []
    all_dialogs[book_id].append(lines)
total_comments_count = calc_comments_count(all_dialogs)

print("------------------")
print("DOC level:")

# Collect.
for k in list(range(10)):
    k_comments = {}
    for book_id, lines in gd_api.filter_comment_with_speaker_at_k(book_path_func=ldc_api.get_book_path, k=k):
        if book_id not in k_comments:
            k_comments[book_id] = []
        k_comments[book_id].append(lines)

    print("COMMENTS with mentioned author at position {k} (%): ".format(k=k),
          round(100.0 * calc_comments_count(k_comments) / calc_comments_count(all_dialogs), 2))

print("------------------")
print("DIALOGUE level:")

# Collect.
for k in [None] + list(range(10)):

    k_dialogs = {}
    for book_id, lines in gd_api.filter_comment_with_speaker_at_k(book_path_func=ldc_api.get_book_path, k=k):
        if book_id not in k_dialogs:
            k_dialogs[book_id] = []
        k_dialogs[book_id].append(lines)

    books_total = len(k_dialogs)

    value = round(100.0 * total_dialogs_count(k_dialogs) / total_dialogs_count(all_dialogs), 2)

    print("At least one segment in DIALOG mention speaker at pos. {k} (% of dialogs): ".format(k=k),
          value,
          "[{}% of books]".format(round(100.0 * len(k_dialogs) / len(all_dialogs))))
