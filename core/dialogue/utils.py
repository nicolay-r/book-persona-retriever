from core.dialogue.speaker_annotation import parse_meta_speaker_id


def iter_by_utterances(dialogue_data):
    """ Iter dialogue data obtained by pg19 API in a form of list of utterances.
    """

    for book_id, data in dialogue_data:

        buffer = []
        curr_speaker_id = None
        for info in data:

            meta, utt = info
            speaker_id = parse_meta_speaker_id(meta)

            # Append the utterance into the buffer.
            if curr_speaker_id is None:
                buffer.append(info)
            elif curr_speaker_id == speaker_id:
                buffer.append(info)
            elif curr_speaker_id != speaker_id:
                # release the buffer.
                if len(buffer) > 0:
                    yield book_id, buffer
                    buffer.clear()
                buffer.append(info)

            curr_speaker_id = speaker_id

        if len(buffer) > 0:
            # release the buffer.
            yield book_id, buffer
            buffer.clear()


def iter_terms_with_speakers(terms, is_term_has_char_func, map_func=None):
    assert(callable(is_term_has_char_func))
    assert(callable(map_func) or map_func is None)

    inds_to_mask = []
    for term_ind, term in enumerate(terms):
        if is_term_has_char_func(term):
            inds_to_mask.append(term_ind)

    if map_func is not None:
        for ind in inds_to_mask:
            terms[ind] = map_func(terms[ind])

    return terms


def mask_text_entities(text, is_term_has_char_func, mask_template="_"):
    terms = iter_terms_with_speakers(is_term_has_char_func=is_term_has_char_func,
                                     terms=text.split(' '),
                                     map_func=lambda _: mask_template)
    return " ".join(terms)
