import itertools

from core.book.terms_stat import TermsStat
from utils_gd import GuttenbergDialogApi
from utils_my import MyAPI


def prefix_analysis(k, p_threshold, books_path_func, filter_func):
    """ Extracting prefixes with their statistics
        for further speaker extraction and assignation.
    """

    gd_api = GuttenbergDialogApi()

    book_dialogs = {}
    for book_id, lines in gd_api.filter_comment_with_speaker_at_k(book_path_func=books_path_func, k=k):
        if book_id not in book_dialogs:
            book_dialogs[book_id] = []

        # We crop part that before speaker.
        for line_ind in range(len(lines)):

            words = lines[line_ind].split()
            cropped = words[:k] if k > 0 else words[1:3]

            if k < len(cropped):
                cropped[k] = '[C]'

            # compose k-gramms.
            lines[line_ind] = '~'.join(cropped).lower()

        # Filter optionally.
        lines = list(filter(filter_func, lines))

        # Collect lines.
        book_dialogs[book_id].append(lines)

    terms_stat = TermsStat()
    for book_id, dialogs in book_dialogs.items():
        text = ' '.join(itertools.chain.from_iterable(dialogs))
        terms_stat.register_doc(doc_id=book_id, terms=text.split())

    # Fill the results.
    tfa_idf = {}
    for term in terms_stat.iter_terms():
        tfa_idf[term] = terms_stat.tfa_idf(term, p_threshold=p_threshold)

    # Filter data.
    return [x for x in tfa_idf.items() if x[1] > 0]


def filter_non_addressed_cases(line, result_sets):
    assert(isinstance(line, str))
    assert(isinstance(result_sets, dict))

    words = line.split('~')

    # We remove `to` in the case of 3 words.
    if len(words) == 3:
        if words[-1] in ["to", "at"]:
            return False
        if words[0] not in result_sets[1]:
            return False

    return True


my_api = MyAPI()
my_api.write_lexicon(analysis_func=prefix_analysis,
                     line_filter=filter_non_addressed_cases)
