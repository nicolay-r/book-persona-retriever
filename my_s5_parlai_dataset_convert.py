import zipstream

from core.utls_parlai_facebook_formatter import format_episode
from utils_ceb import CEBApi
from utils_my import MyAPI


def iter_dataset_lines(my_api):

    ceb_api = CEBApi()
    ceb_api.read_char_map()

    dialog = []
    speakers = []
    for args in my_api.read_dataset(keep_usep=False, split_meta=True):

        if args is None:
            dialog.clear()
            continue

        speakers.append(args[0])
        dialog.append(args[1])

        if len(dialog) < 2:
            continue

        # Provide information about speaker.
        traits = [
            ceb_api.replace_characters_in_text(speakers[1])
        ]

        yield format_episode(request=dialog[0],
                             response=dialog[1],
                             candidates=[dialog[1]],
                             resp_persona_traits=traits).encode()
        yield b"\n"


my_api = MyAPI()
z = zipstream.ZipFile()
z.write_iter('train_original.txt', iter_dataset_lines(my_api))
with open(my_api.dataset_parlai_filepath, "wb") as f:
    for episode_line in z:
        f.write(episode_line)
