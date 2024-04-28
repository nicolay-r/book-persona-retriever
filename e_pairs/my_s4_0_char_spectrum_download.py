import sys
from os.path import join
from core.utils import download, create_dir_if_not_exist
from utils import DATA_DIR

sys.path.append('../')


if __name__ == '__main__':

    create_dir_if_not_exist(DATA_DIR)

    data = {
        join(DATA_DIR, "personalities.txt"): "https://raw.githubusercontent.com/tacookson/data/master/fictional-character-personalities/personalities.txt",
    }

    for target, url in data.items():
        download(dest_file_path=target, source_url=url, desc=target)

    # TODO. Add converter.
