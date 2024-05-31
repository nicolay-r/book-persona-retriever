def filter_relevant_text_comments(is_term_speaker_func, speaker_positions, iter_comments_at_k_func,
                                  cast_to_id_or_none, speakers):
    assert(callable(is_term_speaker_func))
    assert(isinstance(speaker_positions, list))
    assert(callable(iter_comments_at_k_func))
    assert(isinstance(speakers, set))

    for k in speaker_positions:
        for book_id, comments in iter_comments_at_k_func(k):
            for comment in comments:

                # Seek for speaker in a comment.
                for term in comment.split():

                    if not is_term_speaker_func(term):
                        continue

                    # {book_charindex}
                    speaker_id = cast_to_id_or_none(term)
                    if speaker_id is None:
                        continue

                    if speaker_id not in speakers:
                        continue

                    yield comment, [term]
                    break
