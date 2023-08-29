def format_episode(request, response, candidates, resp_persona_traits, resp_persona_prefix="", seed=42):
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(candidates is None)

    common = "Consider you're a character from literature novel book. "

    separator = "\t"
    request = request.replace(separator, "")
    response = response.replace(separator, "")

    if resp_persona_traits[0] is None:
        return common + \
               "What would be the response of this character " \
               "for the following utterance: \"{utterance}\". " \
               "Provide only utterance.".format(utterance=request) \
               + separator + response
    else:
        x = common + \
               "with the following human-level attributes: {traits}. " \
               "What would be the response of this character " \
               "for the following utterance: \"{utterance}\""\
               "Provide only utterance.".format(traits=",".join(resp_persona_traits), utterance=request) \
               + separator + response

        assert(x.count("\t") == 1)
        return x
