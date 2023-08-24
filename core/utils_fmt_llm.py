def format_episode(request, response, candidates, resp_persona_traits, resp_persona_prefix="", seed=42):
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(candidates is None)

    common = "Consider you're a character from literature novel book. "

    request = request.replace("\t", "")

    if resp_persona_traits[0] is None:
        return common + \
               "What would be the response of this character " \
               "for the following utterance: \"{utterance}\". " \
               "Provide only utterance.".format(utterance=request) \
               + "\t" + response
    else:
        return common + \
               "with the following humal-level attributes: {traits}. " \
               "What would be the response of this character " \
               "for the following utterance: \"{utterance}\""\
               "Provide only utterance.".format(traits=",".join(resp_persona_traits), utterance=request) \
               + "\t" + response
