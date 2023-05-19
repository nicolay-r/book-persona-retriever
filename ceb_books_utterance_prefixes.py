import itertools

from core.terms_stat import TermsStat
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def prefix_analysis(k, p_threshold, books_path_func, filter_func):
    """ Extracting prefixes with their statistics
        for further speaker extraction and assignation.
    """

    gd_api = GuttenbergDialogApi()

    book_dialogs = {}
    for book_id, lines in gd_api.filter_utt_with_speaker_at_k(book_path_func=books_path_func, k=k):
        if book_id not in book_dialogs:
            book_dialogs[book_id] = []

        # We crop part that before speaker.
        for i in range(len(lines)):
            bound = k if k > 0 else k+2
            cropped = lines[i].split()[:bound]

            if k < len(cropped):
                cropped[k] = '[C]'

            # compose k-gramms.
            lines[i] = '~'.join(cropped).lower()

        # Filter optionally.
        lines = list(filter(filter_func, lines))

        # Collect lines.
        book_dialogs[book_id].append(lines)

    ts = TermsStat()
    for book_id, dialogs in book_dialogs.items():
        text = ' '.join(itertools.chain.from_iterable(dialogs))
        ts.register_doc(doc_id=book_id, terms=text.split())

    # Fill the results.
    tfa_idf = {}
    for term in ts.iter_terms():
        tfa_idf[term] = ts.tfa_idf(term, p_threshold=p_threshold)

    # Filter data.
    return [x for x in tfa_idf.items() if x[1] > 0]


def filter_non_addressed_cases(line):
    assert(isinstance(line, str))
    words = line.split('~')

    # We remove `to` in the case of 3 words.
    if len(words) == 3:
        return words[-1] not in ["to", "at"]

    return True


my_api = MyAPI()
with open(my_api.prefixes_storage, "w") as out:
    for k in [1, 2, 3]:
        tfa_idf = prefix_analysis(k=k, p_threshold=0.01, books_path_func=my_api.get_book_path,
                                  filter_func=filter_non_addressed_cases)
        sorted_list = sorted(tfa_idf, key=lambda item: item[1], reverse=False)

        for key, v in sorted_list:
            out.write("{prefix},{value}\n".format(prefix=key, value=round(v, 2)))
