import json
import os
from math import ceil
from os.path import exists, dirname


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(
      map(lambda x: lst[x * size:x * size + size],
      list(range(n)))
    )


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
        end = text.index(close_bracket, actual_begin + 1)
    except Exception:
        end = None

    return text[actual_begin + 1:end], end+1


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


class JsonService:

    @staticmethod
    def write(d, target, silent=False):

        # Create target directory if the latter does not exist.
        dir = dirname(target)
        if not exists(dir):
            os.makedirs(dir)

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
