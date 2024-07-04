import json
import os
import sys
import requests
from math import ceil
from os.path import exists

from tqdm import tqdm


def cat_files(source_filepaths, target_filepath):
    assert (isinstance(source_filepaths, list))

    with open(target_filepath, 'w') as outfile:
        for filename in source_filepaths:
            with open(filename) as infile:
                for line in infile:
                    outfile.write(line)


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(
      map(lambda x: lst[x * size:x * size + size],
      list(range(n)))
    )


def count_files_in_folder(folder_path):
    # Initialize a counter for the total number of files
    total_files = 0

    # Iterate over the files in the folder
    for _, _, files in os.walk(folder_path):
        total_files += len(files)

    return total_files


def filter_whitespaces(terms):
    return [term.strip() for term in terms if term.strip()]


def try_extract_entry(text, begin=0, open_bracket="\"", close_bracket="\""):
    assert(isinstance(text, str))

    try:
        actual_begin = text.index(open_bracket, begin)
    except Exception:
        actual_begin = None

    if actual_begin is None:
        return None

    try:
        end = text.index(close_bracket, actual_begin + len(open_bracket))
    except Exception:
        end = None

    if end is None:
        return None

    return text[actual_begin + len(open_bracket):end], end+len(close_bracket)


def extract_all_entries(text, open_bracket, close_bracket, begin=0):

    entry_list = []
    while True:
        result = try_extract_entry(text=text,
                                   open_bracket=open_bracket, close_bracket=close_bracket,
                                   begin=begin)
        if result is None:
            break
        entry, next_char_ind = result
        begin = next_char_ind
        entry_list.append(entry)

    return entry_list


def create_dir_if_not_exist(target_dir):
    if not exists(target_dir):
        os.makedirs(target_dir)


class JsonService:

    @staticmethod
    def write(d, target, silent=False):

        # Create target directory if the latter does not exist.
        create_dir_if_not_exist(target)

        # Do save.
        with open(target, "w") as f:
            if not silent:
                print(f"Save: {target}")
            json.dump(d, f, indent=4, ensure_ascii=False)


class DictService:

    @staticmethod
    def key_to_many_values(pairs_iter, existed=None):
        assert(isinstance(existed, dict) or existed is None)

        d = {} if existed is None else existed
        for k, v in pairs_iter:
            if k not in d:
                d[k] = []
            d[k].append(v)

        return d


def download(dest_file_path, source_url, silent=False, **tqdm_kwargs):
    if not silent:
        print(('Downloading from {src} to {dest}'.format(src=source_url, dest=dest_file_path)))

    sys.stdout.flush()
    datapath = os.path.dirname(dest_file_path)

    if not os.path.exists(datapath):
        os.makedirs(datapath, mode=0o755)

    dest_file_path = os.path.abspath(dest_file_path)

    r = requests.get(source_url, stream=True)
    total_length = int(r.headers.get('content-length', 0))

    with open(dest_file_path, 'wb') as f:
        pbar = tqdm(total=total_length, unit='B', unit_scale=True, **tqdm_kwargs)
        for chunk in r.iter_content(chunk_size=32 * 1024):
            if chunk:  # filter out keep-alive new chunks
                pbar.update(len(chunk))
                f.write(chunk)
