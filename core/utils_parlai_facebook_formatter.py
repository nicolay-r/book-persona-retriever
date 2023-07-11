import random
from utils_my import MyAPI


def format_episode(request, response, candidates, resp_persona_traits=None, resp_persona_prefix="", seed=42):
    """ Serializer for the deprecated formatter proposed by Facebook.
    """
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(isinstance(candidates, list))
    assert(isinstance(seed, int) or seed is None)

    rand = None

    # Performing candidates shuffling
    if seed is not None:
        rand = random.Random(seed)
        rand.shuffle(candidates)

    def __handle_line(l):
        return l.replace('\t', ' ')

    def __fn(a):
        return filter(lambda item: item is not None, a)

    lines = []

    if resp_persona_traits is not None:
        traits = ["{p}persona: I am {t}".format(p=resp_persona_prefix, t=__handle_line(trait))
                  for trait in resp_persona_traits if trait is not None]

        if rand is not None:
            rand.shuffle(traits)

        lines.extend(traits)

    # Main episode content. (Query - Response)
    text = "\n".join(__fn([__handle_line(request)]))
    labels = "\n".join([__handle_line(response)])
    reward = ""
    label_candidates = "|".join([__handle_line(c) for c in candidates])

    lines.append("\t".join([text, labels, reward, label_candidates]))

    return "\n".join(["{} {}".format(i+1, l) for i, l in enumerate(lines)])


def create_candidates_dict(dataset_filepath=None, limit_per_book=1000):
    """ Random candidates selection from the dataset.
        We consider the same "random" selection approach from the ALOHA paper:
            https://arxiv.org/pdf/1910.08293.pdf
    """
    assert(isinstance(limit_per_book, int) and limit_per_book > 0)

    lines = []

    candidates = {}
    for args in MyAPI.read_dataset(keep_usep=False, split_meta=True, dataset_filepath=dataset_filepath):
        if args is None:
            lines.clear()
            continue

        lines.append(args)

        if len(lines) < 2:
            continue

        # Here is type of data we interested in.
        speaker = args[0]
        book_id = int(speaker.split('_')[0])
        if book_id not in candidates:
            candidates[book_id] = []

        target = candidates[book_id]

        if len(target) == limit_per_book:
            # Do not register the candidate.
            continue

        # Consider the potential candidate.
        target.append(args[1])

    return candidates
