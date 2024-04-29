import itertools

from tqdm import tqdm

from api.gd import GuttenbergDialogApi
from core.utils_stat import TermsStat


def prefix_analysis(k, p_threshold, books_path_func, filter_func, **tqdm_kwargs):
    """ Extracting prefixes with their statistics
        for further speaker extraction and assignation.
    """

    gd_api = GuttenbergDialogApi()

    book_dialogs = {}

    pbar = tqdm(**tqdm_kwargs)

    books_seen = set()
    for book_id, lines in gd_api.filter_comment_with_speaker_at_k(book_path_func=books_path_func, k=k):

        if book_id not in book_dialogs:
            book_dialogs[book_id] = []

        # Manually update progress bar with the amount of books.
        books_seen.add(book_id)
        if pbar.n < len(books_seen):
            pbar.update(len(books_seen) - pbar.n)

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

    # Manually update progress bar with the amount of the remaining books.
    # Since some of the books might be skipped.
    pbar.update(pbar.total - pbar.n)

    terms_stat = TermsStat()
    for book_id, dialogs in book_dialogs.items():
        text = ' '.join(itertools.chain.from_iterable(dialogs))
        terms_stat.register(doc_id=book_id, terms=text.split())

    # Fill the results.
    tfa_idf = {}
    for term in terms_stat.iter_terms():
        tfa_idf[term] = terms_stat.tfa_idf(term, p_threshold=p_threshold)

    # Filter data.
    return [item for item in tfa_idf.items() if item[1] > 0]


def filter_non_addressed_cases(line, result_sets):
    assert(isinstance(line, str))
    assert(isinstance(result_sets, dict))

    words = line.split('~')

    # We remove `to` in the case of 3 words.
    if len(words) == 3:
        if words[-1] in ["to", "at"]:
            return False

        # This is a case when such entries as ["to", "at"] actually address
        # convey the connection between utterance and mentioned character
        # in the comment.
        if words[0] not in result_sets[1]:
            return False

    return True


def iter_lexicon_content(speaker_positions, books_path_func, analysis_func,
                         line_filter_func, p_threshold=None, **tqdm_analysis_kwargs):
    assert (isinstance(speaker_positions, list))
    assert (callable(books_path_func))
    assert (callable(analysis_func))
    assert (callable(line_filter_func))
    assert (isinstance(p_threshold, float) or p_threshold is None)

    result_sets = {}

    # For each position K of the character in comment.
    for speaker_position in speaker_positions:

        tqdm_analysis_kwargs.update(
            {"desc": f"Prefix analysis @ speaker position #{speaker_position}/{len(speaker_positions)}"}
        )

        tfa_idf = analysis_func(k=speaker_position, p_threshold=p_threshold if speaker_position > 1 else None,
                                books_path_func=books_path_func,
                                filter_func=lambda value: line_filter_func(value, result_sets),
                                **tqdm_analysis_kwargs)

        # For the pretty output, ordering by `tfa_idf` value.
        sorted_list = sorted(tfa_idf, key=lambda item: item[1], reverse=False)

        if speaker_position > 0:
            for key, value in sorted_list:
                yield "{prefix}".format(prefix=key, value=round(value, 2))

        result_sets[speaker_position] = set([key for key, _ in sorted_list])
