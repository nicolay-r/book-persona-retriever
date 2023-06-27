import zipstream
from utils_my import MyAPI


def format_episode(request, response, candidates, resp_persona_traits=None):
    """ resp_persona_traits:
            used to pass spectrums and (maybe) other main traits known for sure.
    """
    assert(isinstance(request, str))
    assert(isinstance(response, str))
    assert(isinstance(candidates, list))

    def __handle_line(l):
        return l.replace('\t', ' ')

    def __fn(a):
        return filter(lambda item: item is not None, a)

    req_persona = None
    if resp_persona_traits is not None:
        # We follow the Conv2AI format: "Your persona: I am ..."
        req_persona = "\n".join(["your persona: I am {}".format(__handle_line(trait)) for trait in resp_persona_traits])

    text = "text:" + "\n".join(__fn([req_persona, __handle_line(request)]))
    labels = "\n".join(["labels:" + __handle_line(response)])
    label_candidates = "\n".join(["candidates_list:"] + [__handle_line(c) for c in candidates])

    return "\t".join([text, labels, label_candidates, "episode_done:True"]) + "\n"


def iter_dataset_lines(my_api):

    e = []
    for line in my_api.read_dataset():

        if line is None:
            e.clear()
            continue

        # We don't keep meta information.
        prefix = line.split(': ')[0]
        line = line.replace('[USEP]', '')
        e.append(line[len(prefix) + 2:])

        if len(e) < 2:
            continue

        yield format_episode(request=e[0], response=e[1], candidates=[e[1]]).encode()


my_api = MyAPI()
z = zipstream.ZipFile()
z.write_iter('dataset.txt', iter_dataset_lines(my_api))
with open(my_api.dataset_parlai_filepath, "wb") as f:
    for episode_line in z:
        f.write(episode_line)
