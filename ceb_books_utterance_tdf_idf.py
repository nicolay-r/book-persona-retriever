import itertools

from core.terms_stat import TermsStat
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def run(offsets, p_threshold):
    assert(isinstance(offsets, list))

    # Setup API.
    my_api = MyAPI()
    gd_api = GuttenbergDialogApi()

    # Print the total amount of books.
    books_count = my_api.books_count()
    print(books_count)

    # Collect.
    for k in offsets:
        book_dialogs = {}
        for book_id, lines in gd_api.filter_utt_with_speaker_at_k(book_path_func=my_api.get_book_path, k=k):
            if book_id not in book_dialogs:
                book_dialogs[book_id] = []

            # We crop part that before speaker.
            for i in range(len(lines)):
                # compose k-gramms.
                lines[i] = '~'.join(lines[i].split()[:k]).lower()

            # Collect lines.
            book_dialogs[book_id].append(lines)

        ts = TermsStat()
        for book_id, dialogs in book_dialogs.items():
            text = ' '.join(itertools.chain.from_iterable(dialogs))
            ts.register_doc(doc_id=book_id, terms=text.split())

        tfa_idf = {}
        for term in ts.iter_terms():
            tfa_idf[term] = ts.tfa_idf(term, p_threshold=p_threshold)

        # Filter data.
        return [x for x in tfa_idf.items() if x[1] > 0]


# Print the result.
tfa_idf = run(offsets=[1], p_threshold=0.01)
top = sorted(tfa_idf, key=lambda item: item[1], reverse=False)
for k, v in top:
    print(k, round(v, 2))

print(top)
