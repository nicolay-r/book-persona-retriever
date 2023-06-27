import zipstream

from core.utls_parlai_facebook_formatter import format_episode
from utils_my import MyAPI


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
        yield b"\n"


my_api = MyAPI()
z = zipstream.ZipFile()
z.write_iter('train_original.txt', iter_dataset_lines(my_api))
with open(my_api.dataset_parlai_filepath, "wb") as f:
    for episode_line in z:
        f.write(episode_line)
