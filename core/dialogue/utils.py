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
