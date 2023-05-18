from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI

# Setup API.
my_api = MyAPI()
gd_api = GuttenbergDialogApi()

# Print the total amount of books.
books_count = my_api.books_count()
print(books_count)

# Collect.
for k in [None] + list(range(20)):
    book_dialogs = {}
    for book_id, lines in gd_api.filter_utt_with_speaker_at_k(book_path_func=my_api.get_book_path, k=k):
        if book_id not in book_dialogs:
            book_dialogs[book_id] = []
        book_dialogs[book_id].append(lines)

    books_total = len(book_dialogs)
    avg = sum([len(book_dialogs) for book_dialogs in book_dialogs.values()]) / books_count
    print("At least one segment in dialog mention author at position {k} (avg/book): ".format(k=k), round(avg, 2),
          "[{} of {}]".format(books_total, books_count))
