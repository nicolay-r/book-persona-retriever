from utils_my import MyAPI


def filter_query(utterances_it):
    """ Filer those queries from dataset that initiate the dialogue.
    """
    for u in utterances_it:
        if u is None:
            continue
        if not u.startswith(MyAPI.unknown_speaker):
            continue
        yield u


def filter_responses(utterances_it):
    for u in utterances_it:
        if u is None:
            continue
        if u.startswith(MyAPI.unknown_speaker):
            continue
        yield u
