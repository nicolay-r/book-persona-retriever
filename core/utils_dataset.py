def filter_query(utterances_it):
    """ Filer those queries from dataset that initiate the dialogue.
    """

    buffer = []
    for u in utterances_it:
        assert(len(buffer) <= 2)
        if u is None:
            buffer.clear()
            continue
        buffer.append(u)
        if len(buffer) == 1:
            yield u


def filter_responses(utterances_it):

    buffer = []
    for u in utterances_it:
        assert(len(buffer) <= 2)
        if u is None:
            buffer.clear()
            continue
        buffer.append(u)
        if len(buffer) == 2:
            yield u
