def format_episode(request, response, candidates, req_persona_traits=None, resp_persona_traits=None):
    """ Serializer for the deprecated formatter proposed by Facebook.
    """
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(isinstance(candidates, list))

    def __handle_line(l):
        return l.replace('\t', ' ')

    def __fn(a):
        return filter(lambda item: item is not None, a)

    lines = []

    # Traits
    if req_persona_traits is not None:
        traits = ["your persona: I am {}".format(__handle_line(trait)) for trait in req_persona_traits]
        lines.extend(traits)
    if resp_persona_traits is not None:
        traits = ["partner's persona: I am {}".format(__handle_line(trait)) for trait in resp_persona_traits]
        lines.extend(traits)

    # Main episode content. (Query - Response)
    text = "\n".join(__fn([ __handle_line(request)]))
    labels = "\n".join([__handle_line(response)])
    reward = ""
    label_candidates = "|".join([__handle_line(c) for c in candidates])

    lines.append("\t".join([text, labels, reward, label_candidates]))

    return "\n".join(["{} {}".format(i+1, l) for i, l in enumerate(lines)])
