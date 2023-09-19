def format_episode(request, response, candidates, resp_persona_traits=None, resp_persona_prefix="",
                   candidates_random=None):
    """ Serializer for the deprecated formatter proposed by Facebook.
    """
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(isinstance(candidates, list))

    # Performing candidates shuffling
    if candidates_random is not None:
        candidates_random.shuffle(candidates)

    def __handle_line(l):
        return l.replace('\t', ' ')

    def __fn(a):
        return filter(lambda item: item is not None, a)

    lines = []

    # Main episode content. (Query - Response)
    text = "\n".join(__fn([__handle_line(request)]))
    #labels = "\n".join([__handle_line(response)])
    label_candidates = "\nChoose:\n" + "\n".join(
        ["{}{} {}".format("[x]" if c == response else "   ", i, __handle_line(c))
         for i, c in enumerate(candidates)])

    lines.append("\t".join([text, label_candidates]))

    return "\n".join(lines) + "---\n"
